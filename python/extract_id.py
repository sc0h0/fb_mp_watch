from playwright.sync_api import sync_playwright
import re
import datetime
import os
import pytz
import logging

# for proxy
import requests
import re
from bs4 import BeautifulSoup

screenshot_mode = False


def fetch_proxies():
    proxies = []

    # Fetch proxies from spys.me
    response = requests.get("https://spys.me/proxy.txt")
    proxies += re.findall(r"[0-9]+(?:\.[0-9]+){3}:[0-9]+", response.text)

    # Fetch proxies from free-proxy-list.net
    response = requests.get("https://free-proxy-list.net/")
    soup = BeautifulSoup(response.content, 'html.parser')
    for row in soup.select("table tbody tr"):
        tds = row.find_all('td')
        if tds and tds[4].text.strip() == 'elite proxy':  # Filtering for elite proxies
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            proxies.append(f"{ip}:{port}")

    return proxies

# Fetch proxies
proxies = fetch_proxies()
if not proxies:
    raise ValueError("No proxies available")


proxies = fetch_proxies()
successful_load = False

with sync_playwright() as p:
    for proxy in proxies:
        try:
            proxy_server = f"http://{proxy}"  # Format proxy address
            browser = p.chromium.launch(headless=True, slow_mo=1000, proxy={"server": proxy_server})
            page = browser.new_page()
            page.goto('https://www.facebook.com/marketplace/melbourne/search?daysSinceListed=1&query=grange', timeout=30000)
            page.wait_for_timeout(3000)  # Wait for the page to load
            
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
            if matched_ids:
                tz_aet = pytz.timezone('Australia/Sydney')
                now = datetime.datetime.now(tz_aet)
                formatted_date = now.strftime("%Y-%m-%d-%H-%M-%S")
                file_name = os.path.join(extracted_folder_path, f"{formatted_date}_extracted_ids.csv")
                with open(file_name, 'w') as csvfile:
                    for id in matched_ids:
                        csvfile.write(id + '\n')

            successful_load = True
            break  # Exit loop after successful page load
        except Exception as e:
            logging.error(f"Failed to load page with proxy {proxy}: {e}")
        finally:
            browser.close()
    
    if not successful_load:
        logging.error("All proxies failed to load the page.")
