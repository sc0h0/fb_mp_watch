from playwright.sync_api import sync_playwright
import re
import datetime
import os
import pytz


import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("Script started successfully.")

if os.name == 'posix':
    # assume github if unix
    extracted_folder_path = 'data/extracted_id'
elif os.name == 'nt':
    base_path = os.path.dirname(os.path.abspath(__file__))
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
        formatted_date = now.strftime("%Y-%d-%m-%H-%M-%S")
        file_name = os.path.join(extracted_folder_path, f"{formatted_date}_extracted_ids.csv")
        with open(file_name, 'w') as csvfile:  # Using 'w' to overwrite any existing file or 'a' to append if that's the intention
            for id in matched_ids:
                csvfile.write(id + '\n')
            
