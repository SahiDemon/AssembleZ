import scrapy
from scrapy.http import HtmlResponse

class ProductSpider(scrapy.Spider):
    name = "product_info"

    def start_requests(self):
        product_link = input("Enter the product link: ")
        yield scrapy.Request(url=product_link, callback=self.parse)

    def parse(self, response: HtmlResponse):
        title = response.css('.product_title::text').get()
        price = response.css('woocommerce-Price-currencySymbol bdi::text').get()

        print("Title:", title.strip() if title else "N/A")
        print("Price:", "LKR", price.strip() if price else "N/A")

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    settings = {
        'LOG_LEVEL': 'ERROR',
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductSpider)
    process.start()
