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

        category_choice = input("Enter the number of the category you want to scrape (e.g., '1' for Processors): ")

        # Map category choices to URLs and file names
        category_info = {
            '1': {"url": "https://www.nanotek.lk/category/processors", "file_name": "processors.txt"},
            '2': {"url": "https://www.nanotek.lk/category/motherboards", "file_name": "motherboards.txt"},
            '3': {"url": "https://www.nanotek.lk/category/memory-ram", "file_name": "ram.txt"},
            '4': {"url": "https://www.nanotek.lk/category/graphic-cards", "file_name": "graphic_cards.txt"},
            '5': {"url": "https://www.nanotek.lk/category/casings", "file_name": "casings.txt"},
        }

        # Validate category choice
        if category_choice not in category_info:
            if category_choice == '6':
                custom_category_url = input("Enter the custom category URL: ")
                custom_category_name = input("Enter a name for the custom category file (e.g., 'custom.txt'): ")
                category_info['6'] = {"url": custom_category_url, "file_name": custom_category_name}
            else:
                print("Invalid category choice.")
                return

        category_data = category_info[category_choice]
        product_listing_url = category_data["url"]
        file_name = category_data["file_name"]
        yield scrapy.Request(url=product_listing_url, callback=self.parse_product_listing, meta={"file_name": file_name})

    def parse_product_listing(self, response):
        # Extract product links from the listing page
        product_links = response.css('.ty-catPage-productListItem a::attr(href)').getall()

        # Visit each product page
        for product_link in product_links:
            yield scrapy.Request(url=product_link, callback=self.parse_product_page, meta={"file_name": response.meta["file_name"]})

    def parse_product_page(self, response: HtmlResponse):
        # Extract the desired information
        title = response.css('.ty-productTitle::text').get()
        stock = response.css('.ty-special-msg::text').get()
        category = response.css('.ty-productCategory::text').get()
        price = response.css('.ty-price.ty-price-now::text').get()
        product_info = response.css('.ty-productPage-info::text').getall()
        product_info_text = "\n".join(product_info).strip()

        # Construct the full file path for the category
        file_path = response.meta["file_name"]

        with open(file_path, "a", encoding="utf-8") as category_file:
            # Write the information to the category-specific file
            
            category_file.write("\n\nTitle: {}\n".format(title.strip() if title else "N/A"))
            category_file.write("Stock: {}\n".format(stock.strip() if stock else "N/A"))
            category_file.write("Price: LKR {}\n".format(price.strip() if price else "N/A"))
            category_file.write("\nCategory: {}\n".format(category.strip() if category else "N/A"))
            category_file.write("\nProduct Info:\n")
            category_file.write("\n".join(line.strip() for line in product_info_text.splitlines() if line.strip()))
            category_file.write("\n\n")

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Configure Scrapy settings to suppress most logging output
    settings = {
        'LOG_LEVEL': 'ERROR',  # Suppress most log messages
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
