"""3D Model Scraper - Extract and convert 3D models from various sources."""

__version__ = "0.1.0"
__author__ = "TRIPTRAP1"

from .scraper import SketchfabScraper, WoWHeadScraper
from .converters import ModelConverter
from .config import Config

__all__ = [
    "SketchfabScraper",
    "WoWHeadScraper",
    "ModelConverter",
    "Config",
]
