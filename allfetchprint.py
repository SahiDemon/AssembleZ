import scrapy
from scrapy.http import HtmlResponse
import sys
from contextlib import contextmanager

# Define a custom context manager to tee the output to a file and the console
@contextmanager
def tee_output(file, console):
    class TeeOutput:
        def write(self, data):
            file.write(data)
            console.write(data)

        def flush(self):
            file.flush()
            console.flush()

    original_stdout = sys.stdout
    sys.stdout = TeeOutput()

    try:
        yield None
    finally:
        sys.stdout = original_stdout

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

        product_listing_url = category_urls[category_choice]
        yield scrapy.Request(url=product_listing_url, callback=self.parse_product_listing)

    def parse_product_listing(self, response):
        # Extract product links from the listing page
        product_links = response.css('.ty-catPage-productListItem a::attr(href)').getall()

        # Visit each product page
        for product_link in product_links:
            yield scrapy.Request(url=product_link, callback=self.parse_product_page)

    def parse_product_page(self, response: HtmlResponse):
        # Extract the desired information
        title = response.css('.ty-productTitle::text').get()
        stock = response.css('.ty-special-msg::text').get()
        category = response.css('.ty-productCategory::text').get()
        price = response.css('.ty-price.ty-price-now::text').get()
        product_info = response.css('.ty-productPage-info::text').getall()
        product_info_text = "\n".join(product_info).strip()

        
        print()
        print("Title:", title.strip() if title else "N/A")

        print("Stock:", stock.strip() if stock else "N/A")

        print("Price:", "LKR", price.strip() if price else "N/A")
        print()
        print("Category:", category.strip() if category else "N/A")

        print("Product Info:")
        print()
        print("\n".join(line.strip() for line in product_info_text.splitlines() if line.strip()))

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Configure Scrapy settings to suppress most logging output
    settings = {
        'LOG_LEVEL': 'ERROR',  # Suppress most log messages
    }

    # Open a log file for writing
    log_file = open('spider_output.txt', 'w')

    # Use the custom context manager to tee the output to both console and file
    with tee_output(log_file, sys.stdout):
        process = CrawlerProcess(settings=settings)
        process.crawl(ProductSpider)
        process.start()

    # Close the log file
    log_file.close()
