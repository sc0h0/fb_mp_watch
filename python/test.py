from playwright.sync_api import sync_playwright
import os
import re

def login_to_facebook(page, email, password):
    # Check if the login prompt is present
    login_prompt = page.query_selector("text=/log in to continue/i")
    if login_prompt:
        # Fill in the login form
        page.fill('input[name="Email or phone number"]', email)
        page.fill('input[name="Password"]', password)

        # Click the login button
        page.click('button[name="Log In"]')


def run(playwright, log_file):
    fb_email = os.environ['FB_EMAIL']
    fb_password = os.environ['FB_PASSWORD']
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    
    # Open new page
    page = context.new_page()

    # Go to the URL
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange&exact=false')

    login_to_facebook(page, fb_email, fb_password)

    page.wait_for_timeout(5000) 

    page.screenshot(path='screenshot1.png')
    log_file.write("Screenshot 1 saved.\n")

    # Wait for the content to load; adjust the wait time as necessary
    page.wait_for_timeout(5000) 

    page.screenshot(path='screenshot2.png')
    log_file.write("Screenshot 2 saved.\n")

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

    log_file.write("Extracted IDs have been saved to extracted_ids.txt.\n")

    # Close the browser
    browser.close()

# Open the log file
with open('script_log.txt', 'w') as log_file:
    with sync_playwright() as playwright:
        run(playwright, log_file)
