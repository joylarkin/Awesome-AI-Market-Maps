#!/usr/bin/env python3
# This script generates an RSS feed from the README.md file.
"""
Re-builds feeds/AIMarketMaps.xml from every list item that sits
*below* the banner  '## ▦ MARKET MAPS ▦' in README.md
"""
from pathlib import Path
import re, datetime as dt
import html
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.sax.saxutils import escape
import subprocess

def clean_html_entities(text):
    """Clean HTML entities from text while preserving necessary characters."""
    # First decode any existing HTML entities
    text = html.unescape(text)
    # Replace & with 'and' only if it's not part of a word
    text = re.sub(r'\s*&\s*', ' and ', text)
    # Remove any remaining < or > characters
    text = text.replace('<', '').replace('>', '')
    # Remove any remaining HTML entities
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    return text

def safe_xml_text(text):
    """Safely escape text for XML while preserving necessary characters."""
    # First clean any HTML entities
    text = clean_html_entities(text)
    # Then escape for XML, but only if not already escaped
    if '&' in text and not any(entity in text for entity in ['&amp;', '&lt;', '&gt;', '&quot;', '&apos;']):
        text = escape(text)
    return text

def write_xml_element(element, indent=0):
    """Write an XML element with proper indentation and entity handling."""
    result = []
    indent_str = '  ' * indent
    
    # Start tag
    result.append(f"{indent_str}<{element.tag}")
    
    # Attributes
    for key, value in element.attrib.items():
        result.append(f' {key}="{escape(str(value))}"')
    
    if element.text is None and len(element) == 0:
        # Empty element
        result.append(" />\n")
    else:
        # Non-empty element
        result.append(">")
        
        # Text content
        if element.text:
            result.append(safe_xml_text(element.text))
        
        # Child elements
        if len(element) > 0:
            result.append("\n")
            for child in element:
                result.append(write_xml_element(child, indent + 1))
            result.append(indent_str)
        
        # End tag
        result.append(f"</{element.tag}>\n")
    
    return ''.join(result)

def get_git_commit_date(file_path, line_number):
    """Get the commit date for a specific line in a file using git blame."""
    try:
        # Get the commit date for the line using git blame
        cmd = ['git', 'blame', '-L', f'{line_number},{line_number}', '--date=iso', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract the date from the blame output
        # Format: <commit_hash> (<author> <date> <line_number>) <content>
        match = re.search(r'\([^)]*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', result.stdout)
        if match:
            date_str = match.group(1)
            return dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
                
    except subprocess.CalledProcessError as e:
        print(f"[DEBUG] Git blame failed for line {line_number}: {e}")
    except Exception as e:
        print(f"[DEBUG] Unexpected error for line {line_number}: {e}")
    return None

ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / "README.md").read_text(encoding="utf-8")

# ── extract the block that follows the banner until the end of the file ──
block = re.search(
    r"^##\s*▦ MARKET MAPS ▦\s*$\n(.*)",   # multiline + dotall
    readme,
    flags=re.M | re.S,
).group(1)

print(f"[DEBUG] Length of extracted block: {len(block)}")
print("\n[DEBUG] First 10 lines of extracted block:")
print("\n".join(block.splitlines()[:10]))

# ── pull every markdown list item that contains a [title](url) link and associate with nearest preceding #### header ───────────
category = None
categorized_items = []
current_line = 0

# Count lines up to the market maps section
for line in readme.splitlines():
    current_line += 1
    if line.strip() == "## ▦ MARKET MAPS ▦":
        break

# Now process the items
for line in block.splitlines():
    current_line += 1
    header_match = re.match(r"^####\s+(.+)", line)
    if header_match:
        category = header_match.group(1).strip()
    item_match = re.match(r"[-*] \s*\[([^\]]+?)\]\((https?://[^\)]+)\)", line)
    if item_match:
        title, url = item_match.groups()
        # Clean HTML entities at the source, before adding to categorized_items
        cleaned_title = clean_html_entities(title)
        # Get the commit date for this line
        commit_date = get_git_commit_date(ROOT / "README.md", current_line)
        categorized_items.append((cleaned_title, url, category, commit_date))

print(f"[DEBUG] Number of categorized items found: {len(categorized_items)}")
if categorized_items:
    print(f"[DEBUG] First 3 categorized items: {categorized_items[:3]}")

# Debug: print lines with non-http(s) links
print("\n[DEBUG] Lines with non-http(s) links:")
for line in block.splitlines():
    if "](" in line:
        # Find all URLs in the line
        urls = re.findall(r"\]\((.*?)\)", line)
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                print(f"URL: {url}")
                print(f"Line: {line.strip()}\n")

# Sort items by commit date (newest first)
categorized_items.sort(key=lambda x: x[3] if x[3] else dt.datetime.min, reverse=True)

# Create RSS feed using ElementTree
rss = ET.Element('rss', {
    'version': '2.0',
    'xmlns:atom': 'http://www.w3.org/2005/Atom',
    'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
    'xmlns:dc': 'http://purl.org/dc/elements/1.1/'
})

channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = safe_xml_text("Awesome AI Market Maps •• Master AI Market Maps Update Feed")
ET.SubElement(channel, 'link').text = "https://github.com/joylarkin/Awesome-AI-Market-Maps"
ET.SubElement(channel, 'description').text = safe_xml_text("Real-time updates of new AI Market Maps featured in the Awesome-AI-Market-Maps GitHub repository. Follow for new AI Market Maps as they are added. Curated by Joy Larkin (Twitter: @joy).")

# Add atom:link with rel="self" and proper content type
feed_url = "https://raw.githubusercontent.com/joylarkin/Awesome-AI-Market-Maps/main/feeds/AIMarketMaps.xml"
atom_link = ET.SubElement(channel, 'atom:link')
atom_link.set('href', feed_url)
atom_link.set('rel', 'self')
atom_link.set('type', 'application/rss+xml')

ET.SubElement(channel, 'docs').text = "http://www.rssboard.org/rss-specification"
ET.SubElement(channel, 'generator').text = "python-feedgen"
ET.SubElement(channel, 'language').text = "en"

utc_now = dt.datetime.now(dt.timezone.utc)
seen_guids = set()  # Track GUIDs to prevent duplicates

# Keep items in the order they appear in README (newest items are typically added at the top)
for title, url, category, commit_date in categorized_items:
    # Create a unique GUID by combining URL and title
    guid = hashlib.md5(f"{url}{title}".encode()).hexdigest()
    
    # Skip if we've seen this GUID before
    if guid in seen_guids:
        continue
    seen_guids.add(guid)
    
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = safe_xml_text(title)
    ET.SubElement(item, 'link').text = url
    ET.SubElement(item, 'description').text = safe_xml_text(f"{title} - {url}")
    ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = guid
    if category:
        ET.SubElement(item, 'category').text = safe_xml_text(category)
    # Use commit date if available, otherwise use current time
    pub_date = commit_date if commit_date else utc_now
    ET.SubElement(item, 'pubDate').text = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')

# ── write/overwrite the XML file ──────────────────────────────────────────────
out = ROOT / "feeds"
out.mkdir(exist_ok=True)

# Write with explicit XML declaration and stylesheet
with open(out / "AIMarketMaps.xml", 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<?xml-stylesheet type="text/xsl" href="https://raw.githubusercontent.com/joylarkin/Awesome-AI-Market-Maps/main/feeds/rss.xsl"?>\n')
    f.write(write_xml_element(rss)) 
