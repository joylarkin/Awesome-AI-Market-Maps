#!/usr/bin/env python3
"""
Script to extract market map entries from README.md and convert them to CSV format.
"""

import re
import csv
from typing import List, Dict
from collections import OrderedDict

def parse_readme(readme_path: str) -> List[Dict[str, str]]:
    """
    Parse the README.md file and extract all market map entries.

    Returns a list of dictionaries with keys: Date, Category, Author, Title, URL
    """
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the market maps section
    market_maps_start = content.find('▦ MARKET MAPS ▦')
    if market_maps_start == -1:
        raise ValueError("Could not find '▦ MARKET MAPS ▦' section in README")

    # Get everything after the market maps header
    market_maps_section = content[market_maps_start:]

    entries = []
    current_month_year = None
    current_category = None

    # Split by lines
    lines = market_maps_section.split('\n')

    for line in lines:
        # Match month/year headers like "### January 2026" or "### November 2025"
        month_year_match = re.match(r'^###\s+(\w+\s+\d{4})', line)
        if month_year_match:
            current_month_year = month_year_match.group(1)
            continue

        # Match category headers like "#### AI Agents"
        category_match = re.match(r'^####\s+(.+)', line)
        if category_match:
            current_category = category_match.group(1).strip()
            continue

        # Match entry lines like:
        # - [Author — Company - Title - Date](URL)
        # or
        # - [Author - Title - Date](URL)
        entry_match = re.match(r'^-\s+\[([^\]]+)\]\(([^\)]+)\)', line)
        if entry_match and current_month_year and current_category:
            entry_text = entry_match.group(1)
            url = entry_match.group(2)

            # Parse the entry text
            # Format can be:
            # "Author — Company - Title - Date"
            # or "Author - Title - Date"
            parts = entry_text.split(' - ')

            if len(parts) >= 3:
                # Extract date from the end
                date = parts[-1].strip()

                # Extract title (second to last)
                title = parts[-2].strip()

                # Extract author (everything before title)
                author = ' - '.join(parts[:-2]).strip()

                # Create entry
                entry = {
                    'Date': date,
                    'Category': current_category,
                    'Author': author,
                    'Title': title,
                    'URL': url
                }
                entries.append(entry)

    return entries

def read_existing_csv(csv_path: str) -> List[Dict[str, str]]:
    """Read existing CSV file and return list of entries."""
    entries = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
    except FileNotFoundError:
        pass
    return entries

def deduplicate_entries(entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate entries based on URL."""
    seen_urls = set()
    unique_entries = []

    for entry in entries:
        url = entry.get('URL', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_entries.append(entry)

    return unique_entries

def write_csv(entries: List[Dict[str, str]], csv_path: str):
    """Write entries to CSV file."""
    if not entries:
        print("No entries to write!")
        return

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Date', 'Category', 'Author', 'Title', 'URL']
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)

def main():
    readme_path = '/home/user/Awesome-AI-Market-Maps/README.md'
    csv_path = '/home/user/Awesome-AI-Market-Maps/ai_market_maps.csv'

    print("Parsing README.md...")
    new_entries = parse_readme(readme_path)
    print(f"Found {len(new_entries)} entries in README.md")

    print("\nReading existing CSV...")
    existing_entries = read_existing_csv(csv_path)
    print(f"Found {len(existing_entries)} existing entries in CSV")

    print("\nCombining and deduplicating...")
    # Combine new entries with existing ones (new entries first to prefer newer data)
    all_entries = new_entries + existing_entries
    unique_entries = deduplicate_entries(all_entries)
    print(f"After deduplication: {len(unique_entries)} unique entries")

    print(f"\nWriting to {csv_path}...")
    write_csv(unique_entries, csv_path)
    print("Done!")

    # Print some statistics
    print("\n=== Statistics ===")
    print(f"Total entries: {len(unique_entries)}")
    print(f"New entries added: {len(unique_entries) - len(existing_entries)}")

    # Show sample of new entries
    if len(unique_entries) > len(existing_entries):
        print("\n=== Sample of new entries (first 5) ===")
        for i, entry in enumerate(new_entries[:5]):
            print(f"{i+1}. {entry['Date']} - {entry['Category']} - {entry['Title'][:60]}...")

if __name__ == '__main__':
    main()
