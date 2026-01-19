#!/usr/bin/env python3
"""
Script to normalize URLs by adding utm_source parameter and deduplicate entries.
"""

import csv
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict

def normalize_url(url: str) -> str:
    """
    Normalize URL by ensuring it has exactly one utm_source=awesome-ai-market-maps parameter.
    Handles malformed URLs with duplicate or multiple utm_source parameters.
    """
    if not url:
        return url

    # First, clean up any malformed URLs with duplicate utm_source
    # Replace patterns like "?utm_source=X?utm_source=Y" with proper query string
    url = re.sub(r'\?utm_source=[^&?]*\?', '?', url)
    url = re.sub(r'&utm_source=[^&?]*\?', '&', url)

    # Parse the URL
    parsed = urlparse(url)

    # Get existing query parameters
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    # Add or update utm_source (this will replace any existing utm_source)
    query_params['utm_source'] = ['awesome-ai-market-maps']

    # Reconstruct query string
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct URL
    new_parsed = parsed._replace(query=new_query)
    normalized = urlunparse(new_parsed)

    return normalized

def read_csv(csv_path: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of entries."""
    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries

def normalize_and_deduplicate(entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Normalize URLs and remove duplicates.
    When duplicates are found, keep the first occurrence.
    """
    seen_urls = {}  # Maps normalized URL (without utm params) to entry
    unique_entries = []

    for entry in entries:
        original_url = entry.get('URL', '')

        # Normalize the URL
        normalized_url = normalize_url(original_url)

        # Create a base URL for deduplication (without query parameters)
        parsed = urlparse(normalized_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.params:
            base_url += f";{parsed.params}"

        # Check if we've seen this base URL before
        if base_url not in seen_urls:
            # Update entry with normalized URL
            entry['URL'] = normalized_url
            unique_entries.append(entry)
            seen_urls[base_url] = entry

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
    csv_path = '/home/user/Awesome-AI-Market-Maps/ai_market_maps.csv'

    print("Reading CSV...")
    entries = read_csv(csv_path)
    print(f"Found {len(entries)} entries")

    print("\nNormalizing URLs and deduplicating...")
    unique_entries = normalize_and_deduplicate(entries)
    print(f"After normalization and deduplication: {len(unique_entries)} unique entries")
    print(f"Removed {len(entries) - len(unique_entries)} duplicate entries")

    print(f"\nWriting to {csv_path}...")
    write_csv(unique_entries, csv_path)
    print("Done!")

    # Verify no duplicate utm_source parameters
    print("\n=== Verification ===")
    duplicate_utm_count = 0
    for entry in unique_entries:
        url = entry.get('URL', '')
        if url.count('utm_source=awesome-ai-market-maps') > 1:
            duplicate_utm_count += 1
            print(f"WARNING: Duplicate utm_source in: {url}")

    if duplicate_utm_count == 0:
        print("✓ All URLs have exactly one utm_source parameter")
    else:
        print(f"✗ Found {duplicate_utm_count} URLs with duplicate utm_source parameters")

    # Show some examples of normalized URLs
    print("\n=== Sample of normalized URLs (first 5) ===")
    for i, entry in enumerate(unique_entries[:5]):
        print(f"{i+1}. {entry['URL'][:100]}...")

if __name__ == '__main__':
    main()
