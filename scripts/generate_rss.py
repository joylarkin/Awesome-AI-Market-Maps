#!/usr/bin/env python3
# This script generates an RSS feed from the README.md file.
"""
Re-builds feeds/AIMarketMaps.xml from every list item that sits
*below* the banner  '## ▦ MARKET MAPS ▦' in README.md
"""
from pathlib import Path
import re, datetime as dt
from feedgen.feed import FeedGenerator
import html
import hashlib

def clean_html_entities(text):
    """Clean HTML entities from text while preserving necessary characters."""
    # First decode any existing HTML entities
    text = html.unescape(text)
    # Then escape only the characters that need to be escaped in XML
    text = text.replace('&', ' and ')  # Replace & with 'and'
    text = text.replace('<', '')  # Remove <
    text = text.replace('>', '')  # Remove >
    return text

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
for line in block.splitlines():
    header_match = re.match(r"^####\s+(.+)", line)
    if header_match:
        category = header_match.group(1).strip()
    item_match = re.match(r"[-*] \s*\[([^\]]+?)\]\((https?://[^\)]+)\)", line)
    if item_match:
        title, url = item_match.groups()
        categorized_items.append((title, url, category))

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

fg = FeedGenerator()
fg.id("https://github.com/joylarkin/Awesome-AI-Market-Maps")
fg.title("Awesome AI Market Maps •• Master AI Market Maps Update Feed")
fg.link(href="https://github.com/joylarkin/Awesome-AI-Market-Maps")
fg.language("en")
fg.description("Real-time updates of new AI Market Maps featured in the Awesome-AI-Market-Maps GitHub repository. Follow for new AI Market Maps as they are added. Curated by Joy Larkin (Twitter: @joy).")

# Add atom:link with rel="self"
feed_url = "https://raw.githubusercontent.com/joylarkin/Awesome-AI-Market-Maps/main/feeds/AIMarketMaps.xml"
fg.link(href=feed_url, rel="self", type="application/rss+xml")

utc_now = dt.datetime.now(dt.timezone.utc)
seen_guids = set()  # Track GUIDs to prevent duplicates

for title, url, category in reversed(categorized_items):
    # Create a unique GUID by combining URL and title
    guid = hashlib.md5(f"{url}{title}".encode()).hexdigest()
    
    # Skip if we've seen this GUID before
    if guid in seen_guids:
        continue
    seen_guids.add(guid)
    
    fe = fg.add_entry()
    fe.id(guid)
    fe.title(clean_html_entities(title))
    fe.link(href=url)
    fe.published(utc_now)
    description = f"{clean_html_entities(title)} - {url}"
    fe.description(description)
    if category:
        fe.category(term=category)

# ── write/overwrite the XML file ──────────────────────────────────────────────
out = ROOT / "feeds"
out.mkdir(exist_ok=True)
fg.rss_file(out / "AIMarketMaps.xml", pretty=True) 
