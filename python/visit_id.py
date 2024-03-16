import csv
from playwright.sync_api import sync_playwright
import os

def login_to_facebook(page, email, password):
    # Check if the login prompt is present
    login_prompt = page.query_selector("text=/log in to continue/i")
    if login_prompt:
        # Fill in the login form using the ID of the input fields
        page.fill('input#email', email)  # Using the ID selector for the email input field
        page.fill('input#pass', password)  # Using the ID selector for the password input field

        # Attempt to find and click the login button. Adjust the selector as needed.
        login_button = page.query_selector('button[name="login"]')
        if login_button:
            login_button.click()
        else:
            # Log or handle the case where the login button wasn't found
            print("Login button not found.")

def navigate_to_listings(page, listings_csv, log_file):
    base_url = 'https://www.facebook.com/marketplace/item/'

    with open(listings_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            listing_id = row['id']  # Assuming the column name in your CSV is 'id'
            full_url = base_url + listing_id
            log_file.write(f'Navigating to {full_url}\n')
            page.goto(full_url)
            # Here you might add actions to perform on each listing page, like scraping data or taking screenshots
            page.wait_for_timeout(3000)  # Adjust the timeout as necessary


def run(playwright, log_file):
    fb_email = os.environ['FB_EMAIL']
    fb_password = os.environ['FB_PASSWORD']
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    
    # Open new page
    page = context.new_page()

    # Go to Facebook Marketplace search URL
    page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange&exact=false')

    login_to_facebook(page, fb_email, fb_password)

    # Specify the path to your CSV file
    listings_csv = 'data/extracted_ids.csv'

    # Navigate to each listing in the CSV file
    navigate_to_listings(page, listings_csv, log_file)

    # Close the browser
    browser.close()

# Open the log file
with open('script_log.txt', 'w') as log_file:
    with sync_playwright() as playwright:
        run(playwright, log_file)
