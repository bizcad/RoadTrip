import requests
import re
import os

# List of all parts with their exact URL slugs
# Note: The slugs have some inconsistencies (semantid vs senmantic vs semantic), so we use the exact ones.
parts = [
    {"title": "Part 1 - Simple Rules, Complex Behavior", "slug": "semantidintelligence-part1"},
    {"title": "Part 2 - Collective Intelligence", "slug": "semantidintelligence-part2"},
    {"title": "Part 3 - Self-Optimization", "slug": "semantidintelligence-part3"},
    {"title": "Part 4 - The Emergence", "slug": "semantidintelligence-part4"},
    {"title": "Part 5 - Evolution", "slug": "semantidintelligence-part5"},
    {"title": "Part 6 - Global Consensus", "slug": "semantidintelligence-part6"},
    {"title": "Part 7 - The Real Thing", "slug": "senmanticintelligence-part7"}, # typo in slug 'senmantic'
    {"title": "Part 8 - Tools All The Way Down", "slug": "semanticintelligence-part8"}
]

base_url = "https://www.mostlylucid.net/api/raw/"

def clean_markdown(text):
    # The API returns escaped markdown characters (e.g. \#, \*, \[)
    # We need to unescape them for the final file.
    text = text.replace(r'\#', '#')
    text = text.replace(r'\*', '*')
    text = text.replace(r'\`', '`')
    text = text.replace(r'\[', '[')
    text = text.replace(r'\]', ']')
    text = text.replace(r'\_', '_')
    
    # Remove the [TOC] marker if present
    text = text.replace('[TOC]', '')
    
    # Optional: Format the date string which often appears as 2025-11-13T23:00
    text = re.sub(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})', r'\n\n*\1*\n\n', text)
    
    return text

def download_part(part_info):
    slug = part_info["slug"]
    url = f"{base_url}{slug}?language=en"
    filename = f"{part_info['title'].replace(' ', '_').replace(',', '')}.md"
    
    print(f"Downloading {filename} from {url}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        content = clean_markdown(response.text)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Success: Saved to {filename}")
        
    except Exception as e:
        print(f"Error downloading {slug}: {e}")

if __name__ == "__main__":
    for part in parts:
        download_part(part)
