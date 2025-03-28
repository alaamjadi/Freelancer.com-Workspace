import json
import time
import random
import re
import os
import sys
import requests
from bs4 import BeautifulSoup
from typing import Union
import shutil  # To copy files

# Configurations
BASE_URL = "https://www.europarl.europa.eu/meps/en/"

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

# Function to fix reversed emails
def fix_reversed_email(email):
    email = email.replace("[at]", "@").replace("[dot]", ".")  # [at] and [dot] values are not reversed
    email = email[::-1]  # Reverse string
    return email if "@" in email else None  # Ensure valid email format

def clean_href(href: Union[str, None]) -> Union[str, None]:
    """Basic href w"""
    return href.strip() if href else None

# Function to check if a URL is a personal website
def is_personal_website(url):
    return bool(re.match(r"^(https?://)?(www\.)?[\w.-]+\.\w+/?$", url)) # Matches "http(s)://(www.)domain.tld(/)"

def add_to_category(contact, key, value):
    if contact[key] is None:
        contact[key] = []  # Convert None to list before adding
    if value not in contact[key]: # Prevent duplicates
        contact[key].append(value)

def process_member(member):
    try:
        url = f"{BASE_URL}{member['id']}"
        response = requests.get(url, headers={'User-Agent': 'MEP-Scraper/1.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        target_div = soup.find('div', class_='erpl_social-share-horizontal')
        hrefs = [a['href'] for a in target_div.find_all('a')]

        if not hrefs:
            member["status"] = "EUROPARL-NOLINK"
            print("⚠️ Warning: No link has been found for this member!")
            return
        
        contact = member["contact"]

        for item in hrefs:
            if "[at]" in item and "[dot]" in item:  # Likely a reversed email
                fixed_email = fix_reversed_email(item)
                if fixed_email:
                    add_to_category(contact, "email", fixed_email)
            elif any(domain in item for domain in SELECTOR_MAP):
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
        social_media_keys = ["facebook", "instagram", "twitter", "linkedin", "youtube", "tiktok"]
        if all(contact.get(key) is None for key in social_media_keys):
            member["status"] = "EUROPARL-NOSOCIAL"
        else:
            member["status"] = "EUROPARL-SCRAPED"
        return member

def europarl_scraper(mep_raw_json, mep_out_json):
    if not os.path.exists(mep_raw_json):
        print(f"❌ Error: {mep_raw_json} not found!")
        sys.exit(1)

    if os.path.exists(mep_out_json):
        user_input = input(f"⚠️ Caution: {mep_out_json} already exist! Enter 'y/Y' to continue with current file, other to abort> ").lower()
        if user_input != "y":
            print(f"❌ Error: {mep_out_json} already exist! User decided to abort!")
            sys.exit(1)

    else:
        # Copy the original file to preserve data
        shutil.copy(mep_raw_json, mep_out_json)
        print(f"🟢 successfully coppied {mep_raw_json} to {mep_out_json}")
        
    with open(mep_out_json, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        
        for i, member in enumerate(data['meps']):
            print(f"🟢 Processing {i+1}/{len(data['meps'])}: Member ID: {member['id']}")
            
            # Skipping to the next member if it was already processed
            if (member['status'] == "EUROPARL-SCRAPED") or (member['status'] == "EUROPARL-NOSOCIAL"):
                print("⚠️ Warning: User was processed before! Skipping...")
                continue
            
            data['meps'][i] = process_member(member)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.truncate()  
            time.sleep(random.uniform(6, 8)) # Change this value to higher, to avoid getting blocked by security systems
    print("✅ Success: MEP's contact information was scraped from europarl website.")

# Example usage:
mep_raw_josn_file_path = "03_mep-raw.json"   # Replace it with your JSON raw file's path
mep_europarl_scraped_josn_file_path = "05_mep_europarl.json"    # Replace with your JSON output file's path (after scraping https://www.europarl.europa.eu)

europarl_scraper(mep_raw_josn_file_path, mep_europarl_scraped_josn_file_path)
