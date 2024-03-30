from playwright.sync_api import sync_playwright, TimeoutError 
from openai import OpenAI
import datetime
import os
import pytz
import glob
from bs4 import BeautifulSoup

screenshot_mode = True

tz_aet = pytz.timezone('Australia/Sydney')  # 'Australia/Sydney' will automatically handle AEST/AEDT

# Determine the base path relative to the script's location
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the path to the 'data' directory
extracted_folder_path = os.path.join(base_path, '..', 'data/extracted_id')
visited_folder_path = os.path.join(base_path, '..', 'data/visited_id')
matched_folder_path = os.path.join(base_path, '..', 'data/matched_id')
screenshot_path = os.path.join(base_path, '..', 'screenshots')

eid_csv_files = glob.glob(os.path.join(extracted_folder_path, '*.csv'))
vid_csv_files = glob.glob(os.path.join(visited_folder_path, '*.csv'))
mid_csv_files = glob.glob(os.path.join(matched_folder_path, '*.csv'))




def details_are_exclude(details_collected_text):
    # Convert the collected text to lowercase for case-insensitive comparison
    text_lower = details_collected_text.lower()

    # Check if the lowercase text contains
    if 'grange rd' in text_lower or 'grange road' in text_lower or 'near grange' in text_lower:
        return True   
    else:
        return False   
    
def heading_details_keyword(details_collected_text, title_collected_text):
    text_lower = details_collected_text.lower()
    title_lower = title_collected_text.lower()

    # Check if the lowercase text contains 'grange'
    if 'grange' in text_lower or 'grange' in title_lower:
        return True   
    else:
        return False   
    
# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.environ['CHATGPT_API'])


def is_description_heading_about_furniture(description, heading):
    # Use the client to create a chat completion
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Ensure you're using the latest suitable model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
            Consider the following description and title for an item listed on Facebook Marketplace. 
            Your task is to determine if the content suggests that the item is NOT a piece of furniture. 
            The item description is provided first, followed by the title, separated by '|||' for clarity.
            Description: {description}
            |||
            Title: {heading}
            Based on the description and title, is the item a piece of furniture? Please respond with 'yes' if it is a piece of furniture, and 'no' otherwise.
            """}
        ]
    )

    print(f"ChatGPT question: {messages}")

    # Extract and process the answer
    answer = completion.choices[0].message.content.strip().lower()
    print(f"ChatGPT answer: {answer}")
    return "yes" in answer


def visit_ids_with_playwright(item_ids):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=True for headless mode
        page = browser.new_page()

        page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange')
        page.wait_for_timeout(3000)
        if screenshot_mode:
            page.screenshot(path=os.path.join(screenshot_path, 'visit_id_temp_page.png'))

        
        login_prompt = page.query_selector("text=/log in to continue/i")
        page.fill('input#email', os.environ['FB_EMAIL'])  # Using the ID selector for the email input field
        page.fill('input#pass', os.environ['FB_PASSWORD'])  # Using the ID selector for the password input field
        login_button = page.query_selector('button[name="login"]')
        login_button.click()
        page.wait_for_timeout(3000)
        if screenshot_mode:
            page.screenshot(path=os.path.join(screenshot_path, 'visit_id_clicked_login.png'))
            
        
        # initialise a log of visited ids
        visited_ids = set()
        # initialise a log of matched ids
        matched_ids = set()

        for item_id in item_ids:
            # Construct the URL for the item ID
            url = f"https://www.facebook.com/marketplace/item/{item_id}"
            
            # print attempting id
            print(f"Attempting to visit item ID: {item_id}")

            # Navigate to the URL
            page.goto(url)
            if screenshot_mode:
                page.screenshot(path=os.path.join(screenshot_path, 'visit_id_' + item_id + '.png'))
            
            # Selector for the button with aria-label="Close"
            close_button_selector = '[aria-label="Close"]'
            try:
                # Wait for the close button to become visible, with a timeout of 5 seconds
                page.wait_for_selector(close_button_selector, state='visible', timeout=5000)
                page.click(close_button_selector)
                print(f"Close button clicked for item ID: {item_id}")
            except TimeoutError:
                # If the close button doesn't appear within 5 seconds, this block is executed
                print("Close button not found within 5 seconds, continuing with the script.")
                # No need to call `pass` explicitly, but you can if you prefer for readability
                # pass
                
            # wait for safe
            page.wait_for_timeout(2000)
            
            see_more_button_xpath = '//text()[contains(., "...")]/following::span[contains(text(), "See more")][1]'

            see_more_button = page.query_selector(see_more_button_xpath)
            if see_more_button:
                # If the "See more" button exists, click it
                see_more_button.click()
            
            html_content = page.content()
            
            
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            ## capture the details ##
            # Initialize a flag to indicate whether we're currently between the start and end points
            details_collecting = False

            # List to hold all the text between "Details" and "Seller information"
            details_text_between = []
            
            # Check if "Seller information" is in the soup
            if soup.find(string=lambda text: "Seller information" in text):

                # Iterate through all text nodes in the document
                for text_node in soup.find_all(text=True):
                    # If we encounter "Seller information", stop collecting and don't include this text
                    if "Seller information" in text_node:
                        break  # Exit the loop before adding "Seller information" to text_between

                    if details_collecting:
                        details_text_between.append(text_node.strip())
                    
                    # Start collecting after encountering "Details"
                    if "Details" in text_node:
                        details_collecting = True

                # Join the collected text
                details_collected_text = ' '.join(details_text_between)
                

                ## capture the text before details ##
                heading_collecting = False  # Flag to indicate whether we're currently collecting text
                text_after_see_more_before_details = []  # List to hold the desired text

                for text_node in soup.find_all(text=True):
                    # If we encounter "Details", stop collecting
                    if "Details" in text_node:
                        break

                    if heading_collecting:
                        text_after_see_more_before_details.append(text_node.strip())
                    
                    # Start collecting after encountering "See more"
                    if "See more" in text_node:
                        heading_collecting = True
                        text_after_see_more_before_details = []  # Reset the list to exclude text before "See more"

                # Join the collected text
                heading_collected_text = ' '.join(text_after_see_more_before_details)
                
                # if exclude comes back false then it makes sense to use api credits to check if furniture
                if details_are_exclude(details_collected_text) == False and heading_details_keyword(details_collected_text, heading_collected_text) == True:
                    if is_description_heading_about_furniture(details_collected_text, heading_collected_text) == True:
                        print("This is grange furniture")
                        matched_ids.add(item_id)
                        
            # add the visited id to the set
            visited_ids.add(item_id)

                


        # Close the browser after visiting all URLs
        browser.close()
        
        # return the visited ids and matched ids
        return visited_ids, matched_ids
        





if eid_csv_files:
    # Sort the files by their file name with the most recent first
    sorted_eid_csv_files = sorted(eid_csv_files, reverse=True)

    # The first file in the list now has the latest timestamp
    eid_latest_file = sorted_eid_csv_files[0]

    # Open and read the latest CSV file
    with open(eid_latest_file, 'r', encoding='utf-8') as eid_file:
        # Read IDs into a set
        eid_ids = set(eid_file.read().splitlines())
        print(f"Extracted ID: {eid_ids}")
        
    # Initialize vid_ids as an empty set in case there are no vid files
    vid_ids = set()
    matched_ids = set()

    if vid_csv_files:
        # Sort the files by their file name with the most recent first
        sorted_vid_csv_files = sorted(vid_csv_files, reverse=True)

        # The first file in the list now has the latest timestamp
        vid_latest_file = sorted_vid_csv_files[0]

        # Open and read the latest CSV file
        with open(vid_latest_file, 'r', encoding='utf-8') as vid_file:
            # Read IDs into a set
            vid_ids = set(vid_file.read().splitlines())
            
    if mid_csv_files:
        # Sort the files by their file name with the most recent first
        sorted_mid_csv_files = sorted(mid_csv_files, reverse=True)

        # The first file in the list now has the latest timestamp
        mid_latest_file = sorted_mid_csv_files[0]

        # Open and read the latest CSV file
        with open(mid_latest_file, 'r', encoding='utf-8') as mid_file:
            # Read IDs into a set
            matched_ids = set(mid_file.read().splitlines())
    

    # Filter out IDs from eid_ids that are present in vid_ids
    unique_eid_ids = eid_ids - vid_ids
    if unique_eid_ids:
        # order the ids
        unique_eid_ids = sorted(unique_eid_ids)
        returned_vid_ids, returned_mat_ids = visit_ids_with_playwright(unique_eid_ids)
        
        now = datetime.datetime.now(tz_aet)
        formatted_date = now.strftime("%Y-%m-%d-%H-%M-%S")
        
        # Save the visited ids to a CSV file if they exist
        if returned_vid_ids:
            new_vid_ids = vid_ids.union(returned_vid_ids)
            visited_file_name = os.path.join(visited_folder_path, f"{formatted_date}_visited_id.csv")
            with open(visited_file_name, 'a') as csvfile:
                for id in new_vid_ids:
                    csvfile.write(id + '\n')
                    
        # if there are matched ids write them to a csv file
        if returned_mat_ids:
            new_mid_ids = matched_ids.union(returned_mat_ids)
            matched_file_name = os.path.join(matched_folder_path, f"{formatted_date}_matched_id.csv")
            with open(matched_file_name, 'a') as csvfile:
                for id in new_mid_ids:
                    csvfile.write(id + '\n')
        
        


    
        
        
        
