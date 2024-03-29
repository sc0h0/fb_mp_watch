from playwright.sync_api import sync_playwright
import re
import datetime
import os
import pytz


import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("Script started successfully.")


# Determine the base path relative to the script's location
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the path to the 'data' directory
extracted_folder_path = os.path.join(base_path, '..', 'data/extracted_id')
logging.info("Extracted Folder Path: %s", extracted_folder_path)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, slow_mo=1000)
    page = browser.new_page()
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange')
    # wait some time for page to load
    page.wait_for_timeout(3000)
    
    # Regular expression to match the desired URL pattern
    url_pattern = re.compile(r'/marketplace/item/(\d+)')

    # Use Playwright to evaluate JavaScript in the context of the page to get all 'a' tags
    a_tags = page.query_selector_all('a')
    
    # Loop through the 'a' tags and extract the href attribute
    for tag in a_tags:
        href = tag.get_attribute('href')
        match = url_pattern.search(href)
        if match:
            # save to csv in data folder. call the file yyyy-dd-mm-hh-mm-ss_extracted_ids.csv
            tz_aet = pytz.timezone('Australia/Sydney')  # 'Australia/Sydney' will automatically handle AEST/AEDT
            now = datetime.datetime.now(tz_aet)

            formatted_date = now.strftime("%Y-%d-%m-%H-%M-%S")
            file_name = os.path.join(extracted_folder_path, f"{formatted_date}_extracted_id.csv")
            with open( file_name, 'a') as csvfile:
                csvfile.write(match.group(1) + '\n')
            
