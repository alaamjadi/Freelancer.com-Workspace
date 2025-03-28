import json

# Load your JSON data (replace 'meps.json' with your file path)
with open('09_mep_final.json') as f:
    data = json.load(f)

# Define contact categories to analyze
contact_categories = [
    'email', 'website', 'facebook', 'instagram', 'twitter',
    'linkedin', 'youtube', 'tiktok', 'other'
]

# Initialize statistics dictionary
stats = {
    category: {'multiple': 0, 'missing': 0, 'total': 0}
    for category in contact_categories
}
total_members = 0

# Iterate over members and collect data
for member in data['meps']:
    total_members += 1
    contact = member.get('contact', {})
    
    for category in contact_categories:
        value = contact.get(category)
        
        if value is None:
            # Case: Value is explicitly null or missing
            stats[category]['missing'] += 1
        else:
            # Case: Value exists (ensure it's a list)
            if isinstance(value, list):
                count = len(value)
                if count >= 1:
                    stats[category]['total'] += 1
                    if count >= 2:
                        stats[category]['multiple'] += 1
            else:
                # Handle invalid data (optional: log a warning)
                pass

# Generate the Markdown report
report = [
    "# Final Report",
    "",
    "| Items         | Multiple | Missing | Total |",
    f"| :------------ | :------: | :-----: | :---: |"
]

for category in contact_categories:
    # Format category name (capitalize except 'other')
    name = category.capitalize()
    row = (
        f"| **{name}** | {stats[category]['multiple']} | "
        f"{stats[category]['missing']} | {stats[category]['total']} |"
    )
    report.append(row)

report.append(f"| **Member**    |          |         | **{total_members}** |")
# Save to report.md
with open('Report.md', 'w') as f:
    f.write('\n'.join(report))