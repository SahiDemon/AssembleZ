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
        title = response.css('.product-title::text').get()
        stock = response.xpath('//dt[contains(text(), "Stock Availability")]/following-sibling::span/following-sibling::dd/text()').get()
        price = response.css('.price span::text').get()

        # Initialize an empty list to hold product specifications
        product_specs = []
        # Target the table rows within the product description table
        table_rows = response.xpath('//p[contains(b/text(), "Description")]/following-sibling::table[1]/tbody/tr')
        for tr in table_rows:
            # Attempt to extract a pair of non-empty and meaningful data from each row
            # Adjusted to consider the actual text content, ignoring purely whitespace or placeholders
            specs = tr.xpath('td/text()[normalize-space() and not(.="&nbsp;")]').getall()
            specs = [spec.strip() for spec in specs if spec.strip()]
            # Pairing logic adjusted to account for possible variations in table structure
            if specs:
                # Concatenate all specs within a single row for simplicity
                concatenated_specs = ' | '.join(specs)
                product_specs.append(concatenated_specs)

        product_info_text = "\n".join(product_specs).strip()
        image_url = response.css('.tab-pane.active img::attr(src)').get()
        base_url = "https://www.gamestreet.lk/"
        full_image_url = base_url + image_url.strip() if image_url else "N/A"
        print("Image URL:", full_image_url)


        # Display the extracted information
        print("Title:", title.strip() if title else "N/A")
        print("Stock:", stock.strip() if stock else "N/A")
        print("Price:", "LKR", price.strip() if price else "N/A")
        print("Product Specs:")
        print(product_info_text)



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
