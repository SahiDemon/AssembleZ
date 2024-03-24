import asyncio
from playwright.async_api import async_playwright

async def main():
    product_link = input("Enter the product link: ")  # Get the product URL
    async with async_playwright() as p:
        # Launch the browser in headless mode
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()  # Open a new browser page
        await page.goto(product_link, wait_until="networkidle")  # Ensure the page is fully loaded

        # Extract information using Playwright's query selector
        # Use optional chaining (.?) to avoid errors if the element is not found
        title_selector = 'h1.chamaweb-productTitle'
        category_selector = 'h3.chamaweb-productCategory'
        price_selector = 'span.price-div'
        stock_selector = 'span.in-stock-div'
        product_info_selector = 'div.product-desc'
        
        await page.wait_for_selector(title_selector)
        title_element = await page.query_selector(title_selector)
        title = await title_element.text_content() if title_element else "N/A"
        
        await page.wait_for_selector(category_selector)
        category_element = await page.query_selector(category_selector)
        category = await category_element.text_content() if category_element else "N/A"
        
        await page.wait_for_selector(price_selector)
        price_element = await page.query_selector(price_selector)
        price = await price_element.text_content() if price_element else "N/A"
        
        await page.wait_for_selector(stock_selector)
        stock_element = await page.query_selector(stock_selector)
        stock = await stock_element.text_content() if stock_element else "N/A"

        # Display the information
        print(f"Title: {title.strip() if title else 'N/A'}")
        print(f"Category: {category.strip() if category else 'N/A'}")
        print(f"Price: {price.strip() if price else 'N/A'}")
        print(f"Stock: {stock.strip() if stock else 'N/A'}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())