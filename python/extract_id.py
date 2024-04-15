from playwright.sync_api import sync_playwright
import re
import datetime
import os
import pytz
import logging

# Determine the base path relative to the script's location
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the path to the 'data' directory
extracted_folder_path = os.path.join(base_path, '..', 'data/extracted_id')

def run(playwright):
    chromium = playwright.chromium
    # Set up the proxy with authentication using the specified details
    browser = chromium.launch(headless=True, proxy={
        "server": "http://ultra.marsproxies.com:44443",  # Proxy server URL and port
        "username": os.environ['FB_EMAIL'],                       # Proxy username
        "password": os.environ['FB_PASSWORD']            # Proxy password
    })

    # Open a new page
    page = browser.new_page()
    try:
        # Navigate to a test website to confirm proxy is functioning
        page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange', timeout=30000)
        # Optionally, take a screenshot for verification
        page.screenshot(path="ip_address.png")

        # Regular expression to match the desired URL pattern
        url_pattern = re.compile(r'/marketplace/item/(\d+)')
    
        # Use Playwright to evaluate JavaScript in the context of the page to get all 'a' tags
        a_tags = page.query_selector_all('a')
        
        # Initialize an empty list to store the matches
        matched_ids = []
    
        # Loop through the 'a' tags and extract the href attribute
        for tag in a_tags:
            href = tag.get_attribute('href')
            match = url_pattern.search(href)
            if match:
                matched_ids.append(match.group(1))
                logging.info("match id: %s", match)
    
        # If there are matched IDs, write them to a CSV file
        logging.info("matched_ids: %s", matched_ids)
        if matched_ids:
            tz_aet = pytz.timezone('Australia/Sydney')
            now = datetime.datetime.now(tz_aet)  # Ensure 'now' is defined and captures the current time
            formatted_date = now.strftime("%Y-%m-%d-%H-%M-%S")
            file_name = os.path.join(extracted_folder_path, f"{formatted_date}_extracted_ids.csv")
            with open(file_name, 'w') as csvfile:  # Using 'w' to overwrite any existing file or 'a' to append if that's the intention
                for id in matched_ids:
                    csvfile.write(id + '\n')
    
    finally:
        # Ensure the browser is closed after the operation
        browser.close()

