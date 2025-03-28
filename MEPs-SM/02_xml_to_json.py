import xml.etree.ElementTree as ET
import json
import os
import sys

"""
Converts an XML file containing MEP data to a JSON file and adds the necessary contact fields to the structure!
"""

def meps_xml_to_json(xml_file, json_file):
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found!")
        sys.exit(1)
    
    if os.path.exists(json_file):
        user_input = input(f"⚠️ Caution: {json_file} already exist! Enter 'y/Y' to overwrite the current file, other to abort> ").lower()
        if user_input != "y":
            print(f"❌ Error: {json_file} already exist! User decided to abort!")
            sys.exit(1)
    else:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            meps_data = []

            for mep in root.findall('mep'):
                mep_data = {
                    'id': mep.find('id').text if mep.find('id') is not None else None,
                    'fullName': mep.find('fullName').text if mep.find('fullName') is not None else None,
                    'country': mep.find('country').text if mep.find('country') is not None else None,
                    'politicalGroup': mep.find('politicalGroup').text if mep.find('politicalGroup') is not None else None,
                    'nationalPoliticalGroup': mep.find('nationalPoliticalGroup').text if mep.find('nationalPoliticalGroup') is not None else None,
                    'status': 'XML2JSON',
                    'contact': {
                        'email': None,
                        'website': None,
                        'facebook': None,
                        'instagram': None,
                        'twitter': None,
                        'linkedin': None,
                        'youtube': None,
                        'tiktok': None,
                        'other': None,
                    },
                }
                
                meps_data.append(mep_data)

            with open(json_file, 'w') as f:
                json.dump({'meps': meps_data}, f, indent=4)
            
            print(f"✅ Success: MEP data converted to JSON and saved to {json_file}")
        
        except ET.ParseError:
            print(f"❌ Error: Could not parse XML file '{xml_file}'.")
        
        except Exception as e:
            print(f"❌ Error: An unexpected error occurred: {e}")

# Example usage:
xml_file_path = '01_mep-raw.xml'   # Replace with your XML file's path
json_file_path = '03_mep-raw.json'   # Replace with your desired output JSON file's path

meps_xml_to_json(xml_file_path, json_file_path)
