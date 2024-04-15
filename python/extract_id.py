from playwright.sync_api import sync_playwright
import re
import datetime
import os
import pytz
import logging

screenshot_mode = True

fb_email = os.environ['FB_EMAIL']
fb_password = os.environ['FB_PASSWORD']

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("Script started successfully.")

# Determine the base path relative to the script's location
base_path = os.path.dirname(os.path.abspath(__file__))
screenshot_path = os.path.join(base_path, '..', 'screenshots')

# Define the path to the 'data' directory
extracted_folder_path = os.path.join(base_path, '..', 'data/extracted_id')

logging.info("Extracted Folder Path: %s", extracted_folder_path)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, slow_mo=1000)
    page = browser.new_page()
    
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange')
    # wait some time for page to load
    page.wait_for_timeout(3000)
    
    login_prompt = page.query_selector("text=/log in to continue/i")
    page.fill('input#email', fb_email)  # Using the ID selector for the email input field
    page.fill('input#pass', fb_password)  # Using the ID selector for the password input field
    if screenshot_mode:
        page.screenshot(path=os.path.join(screenshot_path, 'extract_id_pre_login.png'))
    page.wait_for_timeout(3000)
    login_button = page.query_selector('button[name="login"]')
    login_button.click()
    page.wait_for_timeout(3000)
    if screenshot_mode:
        page.screenshot(path=os.path.join(screenshot_path, 'extract_id_post_click.png'))
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange')

    if screenshot_mode:
        page.screenshot(path=os.path.join(screenshot_path, 'extract_id_post_login.png'))
    
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
            
