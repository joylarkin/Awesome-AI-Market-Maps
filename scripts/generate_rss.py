#!/usr/bin/env python3
# This script generates an RSS feed from the README.md file.
"""
Re-builds feeds/AIMarketMaps.xml from every list item that sits
*below* the banner  '## ▦ MARKET MAPS ▦' in README.md
"""
from pathlib import Path
import re, datetime as dt
from feedgen.feed import FeedGenerator

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

# ── pull every markdown list item that contains a [title](url) link ───────────
items = re.findall(r"[-*] \s*\[([^\]]+?)\]\((https?://[^\)]+)\)", block)
print(f"[DEBUG] Number of items found: {len(items)}")
if items:
    print(f"[DEBUG] First 3 items: {items[:3]}")

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
fg.title("Awesome AI Market Maps – Master AI Market Maps Update Feed.")  # RSS feed title
fg.link(href="https://github.com/joylarkin/Awesome-AI-Market-Maps")
fg.language("en")
fg.description("Updated list of AI Market Maps from the Awesome-AI-Market-Maps GitHub repository. Follow for new AI Market Maps as they are added. By Joy Larkin (Twitter: @joy).")

utc_now = dt.datetime.now(dt.timezone.utc)
for title, url in reversed(items):
    fe = fg.add_entry()
    fe.id(url)
    fe.title(title)
    fe.link(href=url)
    fe.published(utc_now)          # (or parse dates per item if you add them)                            
    description = f"Learn more about {title} at {url}" if title and url else "No description available."  # Ensure description is populated
    fe.description(description)

# ── write/overwrite the XML file ──────────────────────────────────────────────
out = ROOT / "feeds"
out.mkdir(exist_ok=True)
fg.rss_file(out / "AIMarketMaps.xml", pretty=True) 
