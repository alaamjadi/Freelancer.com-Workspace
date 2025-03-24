import xml.etree.ElementTree as ET
import json

"""
Converts an XML file containing MEP data to a JSON file, splitting full name into first and last names.
Args:
    xml_file (str): Path to the input XML file.
    output_file (str): Path to the output JSON file.
"""

def meps_xml_to_json(xml_file, output_file):
   
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

        with open(output_file, 'w') as f:
            json.dump({'meps': meps_data}, f, indent=4)

        print(f"MEP data converted to JSON and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: XML file '{xml_file}' not found.")
    except ET.ParseError:
        print(f"Error: Could not parse XML file '{xml_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage:
xml_file_path = '01_mep-raw.xml'   # Replace with your XML file's path
output_file_path = '03_mep-raw.json'   # Replace with your desired output JSON file's path

meps_xml_to_json(xml_file_path, output_file_path)