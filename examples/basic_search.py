#!/usr/bin/env python3
"""Basic example: Search and download CC0 models from Sketchfab."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import SketchfabScraper
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<level>{level: <8}</level> | {message}",
)

def main():
    """Run basic example."""
    print("\n" + "="*60)
    print("3D Model Scraper - Basic Example")
    print("="*60 + "\n")

    # Initialize scraper
    with SketchfabScraper() as scraper:
        # Search for CC0 dragon models
        print("\n[1] Searching for CC0 dragon models...")
        models = scraper.search(
            query="dragon",
            license="cc0",
            downloadable=True,
            limit=5,
        )

        if not models:
            print("No models found!")
            return

        print(f"\nFound {len(models)} models:\n")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.get('name')}")
            print(f"     Views: {model.get('viewCount')}")
            print(f"     Likes: {model.get('likeCount')}")
            print(f"     URL: https://sketchfab.com/models/{model.get('uid')}")
            print()

        # Download first model
        if models:
            first_model = models[0]
            model_id = first_model.get("uid")
            model_name = first_model.get("name", "model")

            print(f"\n[2] Attempting to download: {model_name}")
            print("    (Note: Download requires Sketchfab API token for authentication)")
            print(f"    (Set SKETCHFAB_API_TOKEN environment variable or in .env)\n")

            # This will fail without API token, but shows the workflow
            # stl_path = scraper.download_and_convert(model_id, model_name)
            # if stl_path:
            #     print(f"\n[3] Saved: {stl_path}")
            # else:
            #     print("\nDownload failed - API token may be required")

    print("\n" + "="*60)
    print("Example complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
