from playwright.sync_api import sync_playwright
import re

def run(playwright):
    browser = playwright.chromium.launch(headless=True)  # Set headless=False if you want to see the browser UI
    context = browser.new_context()
    
    # Open new page
    page = context.new_page()

    # Go to the URL
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange&exact=false')

    # Wait for the content to load; adjust the wait time as necessary
    page.wait_for_timeout(10000)  # 10 seconds

    # Regular expression to match the desired URL pattern
    url_pattern = re.compile(r'/marketplace/item/(\d+)')

    # Use Playwright to evaluate JavaScript in the context of the page to get all 'a' tags
    a_tags = page.query_selector_all('a')

    # Open a text file to write the extracted IDs
    with open('extracted_ids.txt', 'w') as file:
        for tag in a_tags:
            href = tag.get_attribute('href')
            match = url_pattern.search(href)
            if match:
                # If the URL matches the pattern, write the numeric part to the file
                file.write(match.group(1) + '\n')

    # Close the browser
    browser.close()

    print("Extracted IDs have been saved to extracted_ids.txt.")

with sync_playwright() as playwright:
    run(playwright)
