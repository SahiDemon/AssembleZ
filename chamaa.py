import scrapy
import psycopg2


class ProductSpider(scrapy.Spider):
    name = "product_info2"

    # Define a list of category URLs
    category_urls = [
        "https://store.chamacomputers.lk/category/463",
        "https://store.chamacomputers.lk/category/464",
        "https://store.chamacomputers.lk/category/465",
        "https://store.chamacomputers.lk/category/466",
        "https://store.chamacomputers.lk/category/851",
        
        
    ]

    def start_requests(self):
        # Manually create requests for the first 10 pages of each category
        for category_url in self.category_urls:
            for page_number in range(1, 10):
                page_url = f"{category_url}?page={page_number}"
                yield scrapy.Request(url=page_url, callback=self.parse_product_listing, meta={'category_url': category_url, 'page_number': page_number})

    def parse_product_listing(self, response):
        # Extract product links from the listing page
        product_links = response.css('.ty-catPage-productListItem a::attr(href)').getall()

        # Visit each product page
        for product_link in product_links:
            yield scrapy.Request(url=product_link, callback=self.parse_product_page, meta={'category_url': response.meta['category_url']})

    def parse_product_page(self, response):
        # Extract product details
        title = response.css('.chamaweb-productPage-title::text').get()
        stock = response.css('.in-stock-div[_ngcontent-bei-c14]::text').get()
        category = response.css('.chamaweb-productPage-title h3.chamaweb-productCategory::text').get()
        price = response.css('.price-div[_ngcontent-bei-c14]::text').get()
        product_info = response.css('.product-desc[_ngcontent-bei-c14]::text').getall()
        product_info_text = "\n".join(product_info).strip()

        # Extract image URL
        image_url = response.css('.card-img-top::attr(src)').get()

        # Connect to the Supabase database
        conn = psycopg2.connect(user="postgres.cgojfztufkrckindwkuf", password="Sahiya_448866", host="aws-0-us-west-1.pooler.supabase.com", port="5432", dbname="postgres")
        cursor = conn.cursor()

        # Create a table for the current category if it doesn't exist
        category_table_name = ''.join(e for e in category if e.isalnum())

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