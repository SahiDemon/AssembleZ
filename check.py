import scrapy

class ProcessorSpider(scrapy.Spider):
    name = 'processor_spider'
    start_urls = ['https://www.nanotek.lk/category/processors?page=4']

    def parse(self, response):
        # Extract text within the <h3> element
        no_products_msg = response.css('.ty-catPage-noProducts-msg h3::text').get()
        
        if no_products_msg:
            self.log(f"No Products Message: {no_products_msg}")
        else:
            self.log("No Products message not found")

        # Your scraping logic here
