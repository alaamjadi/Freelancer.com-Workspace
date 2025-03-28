import json
import os
import sys
import shutil
from urllib.parse import urlparse
import tldextract


class DataCleaner:
    def __init__(self):
        self.should_exit = False

    def atomic_save(self, data):
        temp_file = "09_mep_final.tmp"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, "09_mep_final.json")

    def clean(self, member):
        contact = member['contact']

        for key, arrOfElmnts in contact.items():
            if not arrOfElmnts:
                continue
            else:
                arrOfElmnts = list(map(lambda str: str.lower().strip(), arrOfElmnts))
                
                match key:
                    
                    case "email":
                        if len(arrOfElmnts) == 1:
                            continue
                        arrOfElmnts = list(set(arrOfElmnts))
                        
                    case "website":
                        arrOfElmnts = list(set(map(lambda url: (lambda ext: f"https://{ext.domain}.{ext.suffix}")(tldextract.extract(url)), arrOfElmnts)))
                        
                    case "facebook":
                        arrOfElmnts = list(set(
                            map(lambda url: ( "https://facebook.com" +
                                url.replace("profile.php?id=", "")
                                .split('?')[0]
                                .split('#')[0]
                                .rstrip('/')
                                .split('facebook.com')[1]
                                ), arrOfElmnts)))
                    
                    case "instagram":
                        arrOfElmnts = list(set(
                            map(lambda url: ( "https://instagram.com" +
                                url.split('?')[0]
                                .split('#')[0]
                                .rstrip('/')
                                .split('instagram.com')[1]
                                ), arrOfElmnts)))
                    
                    case "twitter":
                        arrOfElmnts = list(set(
                            map(lambda url: ("https://x.com" +
                                url.replace("i/flow/login?redirect_after_login=%\2F", "")
                                .split("/status")[0]
                                .split('?')[0]
                                .split('#')[0]
                                .rstrip('/')
                                .replace("twitter", "x")
                                .split('x.com')[1]
                                ), arrOfElmnts)))
                        
                    case "linkedin":
                        arrOfElmnts = list(set(
                            map(lambda url: ("https://linkedin.com" +
                                url.replace("today/author","in")
                                .split("linkedin.com")[1]
                                .split('?')[0]
                                .split('#')[0]
                                .rstrip('/')
                                ), arrOfElmnts)))
                        
                    case "youtube":
                        arrOfElmnts = list(set(
                            map(lambda url: ("https://www.youtube.com" +
                                url.split("?")[0]
                                .replace("featured", "")
                                .rstrip('/')
                                .replace("user/","@")
                                .replace("youtu.be", "youtube.com")
                                .split("youtube.com")[1]
                                ), arrOfElmnts)))
                        
                    case "tiktok":
                        arrOfElmnts = list(set(
                            map(lambda url: (
                                url.split("?")[0]
                                .rstrip('/')
                                ), arrOfElmnts)))
                    
                    case "other":
                        arrOfElmnts = list(set(
                            map(lambda url: (
                                url.split("?")[0]
                                .rstrip('/')
                                ), arrOfElmnts)))
                    # case _:
                    #     print("default")
                contact[key] = arrOfElmnts
        return member

    def run(self, data):
        try:
            for i, member in enumerate(data['meps']):
                processed_member = self.clean(member)
                data['meps'][i] = processed_member
                self.atomic_save(data)
        finally:
            print(f"🟢 Successfully cleaned and saved the data!")
            
        
input_file = '07_mep_google_smp.json'
output_file = '09_mep_final.json'

if __name__ == "__main__":
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        sys.exit(1)
    if os.path.exists(output_file):
        user_input = input(f"⚠️ Caution: {output_file} already exists! Enter 'y/Y' to continue with current file, other to abort> ").lower()
        if user_input != "y":
            print(f"❌ Error: {output_file} already exists! User decided to abort!")
            sys.exit(1)
    else:
        # Copy the original file to preserve data
        shutil.copy(input_file, output_file)
        print(f"🟢 Successfully copied {input_file} to {output_file}")
        
    with open(output_file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        cleaner = DataCleaner()
        cleaner.run(data)