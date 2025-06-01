#!/usr/bin/env python3
"""
Re-builds feeds/AIMarketMaps.xml from every list item that sits
*below* the banner  '## ▦ MARKET MAPS ▦' in README.md
"""
from pathlib import Path
import re, datetime as dt
from feedgen.feed import FeedGenerator

ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / "README.md").read_text(encoding="utf-8")

# ── extract the block that follows the banner until the next H-level heading ──
block = re.search(
    r"^##\s*▦ MARKET MAPS ▦\s*$\n(.*?)(?:\n## |\Z)",   # multiline + dotall
    readme,
    flags=re.M | re.S,
).group(1)

# ── pull every markdown list item that contains a [title](url) link ───────────
items = re.findall(r"\* \s*\[([^\]]+?)\]\((https?://[^\)]+)\)", block)

fg = FeedGenerator()
fg.id("https://github.com/joylarkin/Awesome-AI-Market-Maps")
fg.title("Awesome AI Market Maps – master feed")
fg.link(href="https://github.com/joylarkin/Awesome-AI-Market-Maps")
fg.language("en")

utc_now = dt.datetime.utcnow()
for title, url in items:
    fe = fg.add_entry()
    fe.id(url)
    fe.title(title)
    fe.link(href=url)
    fe.published(utc_now)          # (or parse dates per item if you add them)
                                                          # Add the description field to each entry
    fe.description(f"Learn more about {title} at {url}")  # Add a default description

# ── write/overwrite the XML file ──────────────────────────────────────────────
out = ROOT / "feeds"
out.mkdir(exist_ok=True)
fg.rss_file(out / "AIMarketMaps.xml", pretty=True) 
