import scrapy
import sqlite3

class ProductSpider(scrapy.Spider):
    name = "product_info"

    # Define a list of category URLs
    category_urls = [
        "https://www.nanotek.lk/category/processors",
        "https://www.nanotek.lk/category/motherboards",
        "https://www.nanotek.lk/category/memory-ram",
        "https://www.nanotek.lk/category/graphic-cards",
        "https://www.nanotek.lk/category/casings",
        
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
        title = response.css('.ty-productTitle::text').get()
        stock = response.css('.ty-special-msg::text').get()
        category = response.css('.ty-productCategory::text').get()
        price = response.css('.ty-price.ty-price-now::text').get()
        product_info = response.css('.ty-productPage-info::text').getall()
        product_info_text = "\n".join(product_info).strip()

        # Extract image URL
        image_url = response.css('.ty-slideContent img::attr(src)').get()

        # Connect to the SQLite database
        conn = sqlite3.connect('scraped_data.db')
        cursor = conn.cursor()

        # Create a table for the current category if it doesn't exist
        category_table_name = ''.join(e for e in category if e.isalnum())

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {category_table_name} (
                id INTEGER PRIMARY KEY,
                title TEXT,
                stock TEXT,
                price TEXT,
                product_info TEXT,
                image_url TEXT
            )
        ''')

        # Check if a product with the same title exists
        cursor.execute(f'SELECT * FROM {category_table_name} WHERE title = ?', (title,))
        existing_product = cursor.fetchone()

        if existing_product:
            # If the product exists, check if stock or price has changed
            existing_stock = existing_product[2]
            existing_price = existing_product[3]
            if stock != existing_stock or price != existing_price:
                # Update stock and price
                cursor.execute(f'''
                    UPDATE {category_table_name}
                    SET stock = ?, price = ?, image_url = ?
                    WHERE title = ?
                ''', (stock, price, image_url, title))
                conn.commit()
                print(f"Data for '{title}' updated in '{category_table_name}' category.")
            else:
                print(f"Data for '{title}' in '{category_table_name}' category is up to date.")
        else:
            # Insert the scraped data into the database
            cursor.execute(f'''
                INSERT INTO {category_table_name} (title, stock, price, product_info, image_url)
                VALUES (?, ?, ?, ?, ?)
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
