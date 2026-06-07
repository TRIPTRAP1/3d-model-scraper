#!/usr/bin/env python3
"""Example: Extract and convert WoWHead character models."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import WoWHeadScraper
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<level>{level: <8}</level> | {message}",
)

def main():
    """Run WoWHead example."""
    print("\n" + "="*70)
    print("3D Model Scraper - WoWHead Example")
    print("="*70 + "\n")

    # Example WoWHead dressing room URL
    # You can find these by visiting: https://www.wowhead.com/dressing-room
    # and sharing the character appearance
    example_url = "https://www.wowhead.com/dressing-room#"

    print("[!] IMPORTANT:")
    print(
        "   1. Visit https://www.wowhead.com/dressing-room#"
    )
    print("   2. Create or load a character appearance")
    print("   3. Click 'Share' and copy the full URL")
    print()

    wowhead_url = input("Enter WoWHead dressing room URL: ").strip()

    if not wowhead_url:
        print("\n[!] No URL provided")
        return

    if "wowhead.com" not in wowhead_url:
        print("\n[!] Invalid URL - must be from wowhead.com")
        return

    # Initialize scraper
    print("\n[*] Initializing WoWHead scraper...")
    scraper = WoWHeadScraper(headless=True)

    try:
        # Extract model URLs
        print("[*] Extracting model URLs from page...\n")
        model_urls = scraper.extract_model_urls(wowhead_url)

        if not model_urls:
            print("[!] No models found. The page may not have loaded correctly.")
            print("    Try visiting the URL in a browser first.")
            return

        # Show found models
        print(f"[✓] Found {len(model_urls)} model(s):\n")
        for i, url in enumerate(model_urls, 1):
            print(f"  {i}. {url[:80]}..." if len(url) > 80 else f"  {i}. {url}")

        # Download and convert
        print(f"\n[*] Downloading and converting {len(model_urls)} model(s)...\n")
        results = []

        for i, url in enumerate(model_urls, 1):
            model_name = f"wowhead_character_part{i}"
            print(f"[{i}/{len(model_urls)}] Processing: {model_name}")

            result = scraper.download_and_convert(url, model_name)
            results.append((model_name, result))

        # Show results
        print("\n" + "="*70)
        print("Results:")
        print("="*70)

        success_count = 0
        for name, result in results:
            if result:
                print(f"[✓] {name} → {result}")
                success_count += 1
            else:
                print(f"[✗] {name} - Failed to convert")

        print(
            f"\n[✓] Successfully processed {success_count}/{len(model_urls)} models"
        )

    finally:
        scraper.close()

    print("\n" + "="*70)
    print("Example complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
