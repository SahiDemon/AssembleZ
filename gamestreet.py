import scrapy
import psycopg2

class ProductSpider(scrapy.Spider):
    name = "gamestreet_product_info"

    def start_requests(self):
        # Define category URLs with descriptive names
        category_urls = {
            'Processors': "https://www.gamestreet.lk/products.php?cat=Mg==&scat=MQ==",
            'Motherboards': "https://www.gamestreet.lk/products.php?cat=Mg==&scat=Mg==",
            'memoryram': "https://www.gamestreet.lk/products.php?cat=Mg==&scat=Mw==",
            'Graphic Cards': "https://www.gamestreet.lk/products.php?cat=Mg==&scat=Ng==",
            'Casings': "https://www.gamestreet.lk/products.php?cat=Mg==&scat=NA==",
        }

        for category_name, url in category_urls.items():
            yield scrapy.Request(url=url, callback=self.parse_product_listing, meta={'category_url': url, 'category_name': category_name})

    def parse_product_listing(self, response):
        product_links = response.css('.product_img a::attr(href)').getall()
        for product_link in product_links:
            full_url = response.urljoin(product_link)
            yield scrapy.Request(url=full_url, callback=self.parse_product_page, meta={'category_url': response.meta['category_url'], 'category_name': response.meta['category_name']})

    def parse_product_page(self, response):
        # Extract product details
        title = response.css('.product-title::text').get()
        stock = response.xpath('//dt[contains(text(), "Stock Availability")]/following-sibling::span/following-sibling::dd/text()').get()
        price = response.css('.price span::text').get()
        product_info_text = self.extract_product_specs(response)
        getimage_url = response.css('.tab-pane.active img::attr(src)').get()
        base_url = "https://www.gamestreet.lk/"
        image_url = base_url + getimage_url.strip() if getimage_url else "N/A"

        category_name = response.meta['category_name']  # Now category_name is defined via meta

        # Connect to the Supabase database
        conn = psycopg2.connect(user="postgres.cgojfztufkrckindwkuf", password="Sahiya_448866", host="aws-0-us-west-1.pooler.supabase.com", port="5432", dbname="postgres")
        cursor = conn.cursor()

        # Ensure the schema exists; create it if it doesn't
        schema_name = "gamestreet" 
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name};')
        conn.commit()

        # Now specify the schema in your table name
        category_table_name = f"{schema_name}.{''.join(e for e in category_name if e.isalnum())}"

        # Create a table for the current category if it doesn't exist
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {category_table_name} (
                id SERIAL PRIMARY KEY,
                title TEXT,
                stock TEXT,
                price TEXT,
                product_info TEXT,
                image_url TEXT
            )
        ''')

        # Check if a product with the same title exists
        cursor.execute(f'SELECT * FROM {category_table_name} WHERE title = %s', (title,))
        existing_product = cursor.fetchone()

        if existing_product:
            # If the product exists, check if stock or price has changed
            existing_stock = existing_product[2]
            existing_price = existing_product[3]
            if stock != existing_stock or price != existing_price:
                # Update stock and price
                cursor.execute(f'''
                    UPDATE {category_table_name}
                    SET stock = %s, price = %s, image_url = %s
                    WHERE title = %s
                ''', (stock, price, image_url, title))
                conn.commit()
                print(f"Data for '{title}' updated in '{category_table_name}' category.")
            else:
                print(f"Data for '{title}' in '{category_table_name}' category is up to date.")
        else:
            # Insert the scraped data into the database
            cursor.execute(f'''
                INSERT INTO {category_table_name} (title, stock, price, product_info, image_url)
                VALUES (%s, %s, %s, %s, %s)
            ''', (title, stock, price, product_info_text, image_url))
            conn.commit()
            print(f"Data for '{title}' inserted into '{category_table_name}' category.")

        # Close the database connection
        conn.close()


    def extract_product_specs(self, response):
        # Method to extract product specifications
        product_specs = []
        table_rows = response.xpath('//p[contains(b/text(), "Description")]/following-sibling::table[1]/tbody/tr')
        for tr in table_rows:
            specs = tr.xpath('td/text()[normalize-space() and not(.="&nbsp;")]').getall()
            specs = [spec.strip() for spec in specs if spec.strip()]
            if specs:
                concatenated_specs = ' | '.join(specs)
                product_specs.append(concatenated_specs)
        return "\n".join(product_specs).strip()

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    settings = {'LOG_LEVEL': 'ERROR'}
    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
