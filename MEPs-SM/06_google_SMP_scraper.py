import json
import time
import random
import re
import os
import signal
import sys
from typing import Union
import shutil  # To copy files
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse


# Configuration
GOOGLE_URL = "https://www.google.com/search?q="

SELECTOR_MAP = {
    "facebook.com": "facebook",
    "fb.com": "facebook",
    "instagram.com": "instagram",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "linkedin.com": "linkedin",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "tiktok.com": "tiktok"
}

class GoogleScraper:
    def __init__(self):
        self.should_exit = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.driver = self.init_driver()
        self.total_members = 0

    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--headless")  # This has been removed to see the procedure during scraping
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def exit_gracefully(self, signum, frame):
        print("\n🚨 Received interrupt signal. Performing safe shutdown...")
        self.should_exit = True
        try:
            self.driver.quit()
        except Exception:
            pass
        sys.exit(1)

    def atomic_save(self, data):
        """Prevent database corruption during saves"""
        temp_file = "07_mep_google_smp.tmp"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, "07_mep_google_smp.json")

    def process_member(self, member):
        if self.should_exit:
            return member
        urls = []
        try:
            # query = f"{member['fullName']}"  # More general query
            query = f"{member['fullName']} EUROPARL"
            self.driver.get(GOOGLE_URL + query.replace(' ', '+'))
            
            # Target Google's new social media section
            try:
                social_section = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div[data-attrid='kc:/common/topic:social media presence']"
                    ))
                )
            except TimeoutException:
                print(f"⚠️ Warning: No social media section found for {member['id']}")
                return member

            # Process only social media section links
            g_links = social_section.find_elements(By.TAG_NAME, "g-link")

            for g_link in g_links:
                if self.should_exit:
                    break
                
                try:
                    # Ensure element visibility
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                        g_link
                    )
                    time.sleep(0.3)  # Allow rendering
                    
                    # Get nested a-tag
                    a_tag = WebDriverWait(g_link, 1).until(
                        EC.presence_of_element_located((By.TAG_NAME, "a"))
                    )
                    
                    # adding each url to the urls
                    urls.append(a_tag.get_attribute("href"))

                except Exception as e:
                    continue  # Skip failed elements
            
            if not urls:
                member["status"] = "GOOGLE-SMP-NOLINK"
                return
            
            contact = member["contact"]
            for item in urls:
                if any(domain in item for domain in SELECTOR_MAP):
                    for domain, category in SELECTOR_MAP.items():
                        if domain in item:
                            add_to_category(contact, category, item)
                elif is_personal_website(item):
                    add_to_category(contact, "website", item)
                else:
                    add_to_category(contact, "other", item)

        except Exception as e:
            print(f"❌ Error: Error processing {member['id']}: {str(e)}")
        
        finally:
            member['status'] = "GOOGLE-SMP-SCRAPED"
            return member

    def run(self, data):
        self.total_members = len(data['meps'])
        
        try:
            time.sleep(10)  # Initial delay of 8 seconds to pass the Google agreements, captcha and, browser language setting
            
            for i, member in enumerate(data['meps']):
                print(f"🟢 Processing {i+1}/{self.total_members}: Member ID: {member['id']}")
                if self.should_exit:
                    print("\n🚨 Early exit triggered. Saving in progress...")
                    break

                # Skipping to the next member if it was already processed
                if member['status'] == "GOOGLE-SMP-SCRAPED":
                    print("⚠️ Warning: User was processed before! Skipping...")
                    continue

                processed_member = self.process_member(member)
                data['meps'][i] = processed_member
                
                # Save the progress
                self.atomic_save(data)
                time.sleep(random.uniform(6.5, 10.8))

        finally:
            try:
                self.driver.quit()
            except Exception:
                pass

def is_personal_website(url):
    return bool(re.match(r"^(https?://)?(www\.)?[\w.-]+\.\w+/?$", url)) # Matches "http(s)://(www.)domain.tld(/)"

def add_to_category(contact, key, value):
    if contact[key] is None:
        contact[key] = []  # Convert None to list before adding
    if value not in contact[key]: # Prevent duplicates
        contact[key].append(value)

# Example usage:
mep_europarl_josn_file_path = "05_mep_europarl.json"    # Replace it with your JSON europarl scraped file's path
mep_google_scraped_json_file_path = "07_mep_google_smp.json"    # Replace with your JSON output file's path (after scraping https://www.google.com)

if __name__ == "__main__":    
    if not os.path.exists(mep_europarl_josn_file_path):
        print(f"❌ Error: {mep_europarl_josn_file_path} not found!")
        sys.exit(1)
    
    if os.path.exists(mep_google_scraped_json_file_path):
        user_input = input(f"⚠️ Caution: {mep_google_scraped_json_file_path} already exist! Enter 'y/Y' to continue with current file, other to abort> ").lower()
        if user_input != "y":
            print(f"❌ Error: {mep_google_scraped_json_file_path} already exist! User decided to abort!")
            sys.exit(1)
    else:
        # Copy the original file to preserve data
        shutil.copy(mep_europarl_josn_file_path, mep_google_scraped_json_file_path)
        print(f"🟢 successfully coppied {mep_europarl_josn_file_path} to {mep_google_scraped_json_file_path}")
    
    # Start reading the json file and processing members
    with open(mep_google_scraped_json_file_path, 'r+', encoding='utf-8') as f:
        data = json.load(f)
    scraper = GoogleScraper()
    scraper.run(data)