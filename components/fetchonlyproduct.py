import scrapy
from scrapy.http import HtmlResponse

# Define the Spider class
class ProductSpider(scrapy.Spider):
    name = "product_info"

    def start_requests(self):
        # Ask the user for the product link
        product_link = input("Enter the product link: ")
        yield scrapy.Request(url=product_link, callback=self.parse)

    def parse(self, response: HtmlResponse):
        # Extract the desired information
        title = response.css('h1.chamaweb-productTitle::text').get()
        stock = response.css('span.in-stock-div::text').get()
        category = response.css('h3.chamaweb-productCategory::text').get()
        price = response.css('span.price-div::text').get()
        product_info = response.css('div.product-desc::text').getall()
        product_info_text = "\n".join(product_info).strip()

        # Display the information
        print("Title:", title.strip() if title else "N/A")
        print()  
        print("Stock:", stock.strip() if stock else "N/A")
        print()  
        print("Category:", category.strip() if category else "N/A")
        print() 
        print("Price:", "LKR", price.strip() if price else "N/A")
        
        print("Product Info:")
        print()  
        print("\n".join(line.strip() for line in product_info_text.splitlines() if line.strip()))  # Remove spaces between lines
       


# Run the spider
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Configure Scrapy settings to suppress most logging output
    settings = {
        'LOG_LEVEL': 'ERROR',  # Suppress most log messages
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
