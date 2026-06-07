#!/usr/bin/env python3
"""Launch the Terminal User Interface for the 3D model scraper."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tui import ScraperTUI

if __name__ == "__main__":
    tui = ScraperTUI()
    tui.run()
