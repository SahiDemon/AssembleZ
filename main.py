import scrapy
import sqlite3

class ProductSpider(scrapy.Spider):
    name = "product_info"

    def start_requests(self):
        # Ask the user for the category choice
        print("Choose a category:")
        print("1. Processors")
        print("2. Motherboards")
        print("3. RAM")
        print("4. Graphic Cards")
        print("5. Casings")
        print("6. Custom")

        category_choice = input("Enter the number of the category you want to scrape from nanotek.lk: ")

        # Map category choices to URLs
        category_urls = {
            '1': "https://www.nanotek.lk/category/processors",
            '2': "https://www.nanotek.lk/category/motherboards",
            '3': "https://www.nanotek.lk/category/memory-ram",
            '4': "https://www.nanotek.lk/category/graphic-cards",
            '5': "https://www.nanotek.lk/category/casings",
        }

        # Validate category choice
        if category_choice not in category_urls:
            if category_choice == '6':
                custom_category_url = input("Enter the custom category URL: ")
                category_urls['6'] = custom_category_url
            else:
                print("Invalid category choice.")
                return

        category_url = category_urls[category_choice]

        # Manually create requests for the first 10 pages
        for page_number in range(1, 10):
            page_url = f"{category_url}?page={page_number}"
            yield scrapy.Request(url=page_url, callback=self.parse_product_listing, meta={'page_number': page_number})

    def parse_product_listing(self, response):
        # Extract product links from the listing page
        product_links = response.css('.ty-catPage-productListItem a::attr(href)').getall()

        # Visit each product page
        for product_link in product_links:
            yield scrapy.Request(url=product_link, callback=self.parse_product_page)

    def parse_product_page(self, response):
        # Extract product details
        title = response.css('.ty-productTitle::text').get()
        stock = response.css('.ty-special-msg::text').get()
        category = response.css('.ty-productCategory::text').get()
        price = response.css('.ty-price.ty-price-now::text').get()
        product_info = response.css('.ty-productPage-info::text').getall()
        product_info_text = "\n".join(product_info).strip()

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
                product_info TEXT
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
                    SET stock = ?, price = ?
                    WHERE title = ?
                ''', (stock, price, title))
                conn.commit()
                print(f"Data for '{title}' updated in '{category_table_name}' category.")
            else:
                print(f"Data for '{title}' in '{category_table_name}' category is up to date.")
        else:
            # Insert the scraped data into the database
            cursor.execute(f'''
                INSERT INTO {category_table_name} (title, stock, price, product_info)
                VALUES (?, ?, ?, ?)
            ''', (title, stock, price, product_info_text))
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
