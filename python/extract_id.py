from playwright.sync_api import sync_playwright
import os
import re
import csv

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

def log_input_fields(page, log_file):
    # Find all input elements on the page
    inputs = page.query_selector_all('input')

    # Log a header for clarity
    log_file.write("Logging all text input fields found on the page:\n")

    for input_element in inputs:
        # Check if the input element is a text field
        if input_element.get_attribute('type') in ['text', 'email', 'password']:
            # Get useful attributes to uniquely identify the input field
            input_name = input_element.get_attribute('name')
            input_id = input_element.get_attribute('id')
            input_class = input_element.get_attribute('class')

            # Log the details of the input field
            log_file.write(f"Input Field - Name: {input_name}, ID: {input_id}, Class: {input_class}\n")


# Function to scroll to the bottom of the page
def scroll_to_bottom(page):
    try:
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for page load or any possible navigation to complete
            page.wait_for_timeout(5000)  # Adjust based on your page's load time

            try:
                # Use try-except to catch any evaluation errors due to navigation or page changes
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            except playwright._impl._errors.Error as e:
                print(f"Error during scroll evaluation: {e}")
                # If an error occurs, wait a bit and then try to get the new scroll height again
                page.wait_for_timeout(1000)  # Short wait before retry
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

    except playwright._impl._errors.Error as e:
        print(f"Encountered an error: {e}")
        # Handle the error or retry the entire scroll_to_bottom function as needed
        # Consider adding a retry mechanism or exiting the function if the page context is lost


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
    #log_input_fields(page, log_file)

    page.wait_for_timeout(5000) 

    scroll_to_bottom(page)

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

    with open('data/extracted_ids.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write a header row if desired
        csvwriter.writerow(['id'])
        
        for tag in a_tags:
            href = tag.get_attribute('href')
            match = url_pattern.search(href)
            if match:
                # If the URL matches the pattern, write the numeric part to the CSV file
                csvwriter.writerow([match.group(1)])

    log_file.write("Extracted IDs have been saved to extracted_ids.txt.\n")

    # Close the browser
    browser.close()

# Open the log file
with open('script_log.txt', 'w') as log_file:
    with sync_playwright() as playwright:
        run(playwright, log_file)
