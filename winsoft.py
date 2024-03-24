import scrapy
import psycopg2

class ProductSpider(scrapy.Spider):
    name = "product_info"

    category_urls = {
        "motherboards": "https://www.winsoft.lk/product-category/core-components/motherboards",
        "memory": "https://www.winsoft.lk/product-category/core-components/memory",
        "graphics-cards": "https://www.winsoft.lk/product-category/core-components",
        "computer-casings": "https://www.winsoft.lk/product-category/core-components/computer-casings",
        "processors": "https://www.winsoft.lk/product-category/core-components/processors",
        # Add more category URLs as needed
    }

    def start_requests(self):
        # Manually create requests for the first 10 pages of each category
        for category_name, category_url in self.category_urls.items():
            for page_number in range(1, 10):
                # Adjust URL generation logic for the new site if necessary
                page_url = f"{category_url}/page/{page_number}"
                yield scrapy.Request(url=page_url, callback=self.parse_product_listing, meta={'category_url': category_url, 'page_number': page_number, 'category_name': category_name})

    def parse_product_listing(self, response):
        # Extract product links from the listing page of the new site
        product_links = response.css('.product-element-top .wd-quick-shop a::attr(href)').getall()

        # Visit each product page
        for product_link in product_links:
            # Add the logic to visit each product page
            yield scrapy.Request(url=product_link, callback=self.parse_product_page, meta={'category_url': response.meta['category_url']})

    def parse_product_page(self, response):
        # Extract product details from the product page of the new site
        title = response.css('.product_title.entry-title.wd-entities-title::text').get()
        stock = "in stock"
        category = response.meta['category_url']
        price = response.css('.price span.woocommerce-Price-amount.amount bdi::text').get()
        product_info = response.css('//div[@class="woocommerce-product-details__short-description"]/ul/li/text()').getall()
        product_info_text = "\n".join(product_info).strip()
        image_url = response.css('.figure.woocommerce-product-gallery__image img::attr(data-src)').get()

        # Connect to the database
        conn = psycopg2.connect(user="postgres.cgojfztufkrckindwkuf", password="Sahiya_448866", host="aws-0-us-west-1.pooler.supabase.com", port="5432", dbname="postgres")
        cursor = conn.cursor()

        # Ensure the schema exists; create it if it doesn't
        schema_name = "winsoft"  # Change this to match your schema name
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name};')
        conn.commit()

        # Specify the schema in your table name
        category_table_name = f"{schema_name}.{''.join(e for e in category if e.isalnum())}"

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
            existing_stock = existing_product[2]
            existing_price = existing_product[3]
            if stock != existing_stock or price != existing_price:
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
            cursor.execute(f'''
                INSERT INTO {category_table_name} (title, stock, price, product_info, image_url)
                VALUES (%s, %s, %s, %s, %s)
            ''', (title, stock, price, product_info_text, image_url))
            conn.commit()
            print(f"Data for '{title}' inserted into '{category_table_name}' category.")

        # Close the database connection
        conn.close()

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Configure Scrapy settings to suppress most logging output
    settings = {
        'LOG_LEVEL': 'ERROR',  # Suppress most log messages
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
