import scrapy

class ProductSpider(scrapy.Spider):
    name = "product_info"

    def start_requests(self):
        # Ask the user for the product listing URL
        product_listing_url = input("Enter the product listing URL: ")
        yield scrapy.Request(url=product_listing_url, callback=self.parse)

    def parse(self, response):
        # Extract product names and prices
        product_blocks = response.css('.ty-productBlock')
        product_info_list = []

        for product_block in product_blocks:
            
            name = product_block.css('.ty-productBlock-title h1::text').get()
            price = product_block.css('.ty-productBlock-price-retail::text').get()
            

            if name and price:
                product_info = {
                    "name": name.strip(),
                    "price": price.strip(),
                }
                product_info_list.append(product_info)

        # Print the product information
        for product_info in product_info_list:
            print(f"Name: {product_info['name']}, Price: {product_info['price']}")

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Configure Scrapy settings to suppress most logging output
    settings = {
        'LOG_LEVEL': 'ERROR',  # Suppress most log messages
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
