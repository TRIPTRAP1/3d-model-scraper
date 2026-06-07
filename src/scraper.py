"""Main scraper classes for Sketchfab and WoWHead."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from .api_client import APIClient
from .config import get_config
from .converters import ModelConverter
from .utils import extract_filename_from_url, sanitize_filename


class SketchfabScraper:
    """
    Scraper for Sketchfab models using public API.
    
    API Docs: https://docs.sketchfab.com/data-api/v3/index.html
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Sketchfab scraper.

        Args:
            api_token: Optional API token for authenticated requests
        """
        config = get_config()
        self.api_token = api_token or config.sketchfab_api_token
        self.api_client = APIClient(
            base_url=config.sketchfab_api_url,
            api_token=self.api_token,
            timeout=config.request_timeout,
            rate_limit_delay=config.request_delay,
        )
        self.download_dir = Path(config.download_dir)
        self.output_dir = Path(config.output_dir)
        self.converter = ModelConverter()

    def search(
        self,
        query: str,
        license: Optional[str] = None,
        downloadable: bool = True,
        sort_by: str = "-likeCount",
        limit: int = 24,
        cursor: Optional[str] = None,
    ) -> List[Dict]:
        """
        Search for 3D models on Sketchfab.

        Args:
            query: Search query
            license: Filter by license (e.g., 'cc0', 'cc-by')
            downloadable: Only return downloadable models
            sort_by: Sort order (-likeCount, -viewCount, -publishedAt)
            limit: Maximum results
            cursor: Cursor for pagination

        Returns:
            List of model metadata dictionaries
        """
        params = {
            "type": "models",
            "q": query,
            "sort": sort_by,
            "count": min(limit, 100),  # Max 100 per request
        }

        if downloadable:
            params["downloadable"] = "true"

        if license:
            # License IDs on Sketchfab
            license_map = {
                "cc0": "7c23a1ba438d4306920229c12afcb5f9",
                "cc-by": "b9ddc50ae5de4f76934129127b9da246",
                "cc-by-sa": "19e41217773b4dd8b12df7aa618f89c4",
                "cc-by-nc": "e038bcc0ac384c0b8ef05078c30f4d0a",
                "cc-by-nc-sa": "7559382baf674245aeb0a2dbbd66aec7",
            }
            if license.lower() in license_map:
                params["licenses"] = license_map[license.lower()]

        if cursor:
            params["cursor"] = cursor

        logger.info(f"Searching Sketchfab: {query} (limit: {limit})")

        try:
            response = self.api_client.get("/search", params=params)
            data = response.json()

            models = data.get("results", [])
            logger.info(f"Found {len(models)} models")

            return models

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model.

        Args:
            model_id: Model ID (32-char hex string)

        Returns:
            Model metadata or None if not found
        """
        try:
            response = self.api_client.get(f"/models/{model_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None

    def get_model_download_url(self, model_id: str) -> Optional[str]:
        """
        Get the download URL for a model file.

        Args:
            model_id: Model ID

        Returns:
            Download URL or None if not available
        """
        if not self.api_token:
            logger.warning("API token required to get download URL")
            return None

        try:
            response = self.api_client.get(f"/models/{model_id}/download")
            data = response.json()

            # Try to get GLTF first, then GLB
            if "gltf" in data and "url" in data["gltf"]:
                return data["gltf"]["url"]
            elif "glb" in data and "url" in data["glb"]:
                return data["glb"]["url"]

            logger.warning(f"No download URL found for {model_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None

    def download_model(
        self,
        download_url: str,
        model_name: str = "model",
    ) -> Optional[Path]:
        """
        Download a model file.

        Args:
            download_url: URL to download from
            model_name: Name for the downloaded file

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            filename = sanitize_filename(model_name)
            filepath = self.download_dir / filename

            self.api_client.download(download_url, str(filepath))
            return filepath

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def download_and_convert(
        self,
        model_url: str,
        model_name: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Download a model and convert to STL.

        Args:
            model_url: URL or ID of model
            model_name: Optional name for the model

        Returns:
            Path to converted STL file or None if failed
        """
        try:
            # Extract model ID from URL if needed
            if "sketchfab.com" in model_url:
                model_id = model_url.split("/")[-1]
            else:
                model_id = model_url

            # Get model info
            info = self.get_model_info(model_id)
            if not info:
                logger.error(f"Could not get model info for {model_id}")
                return None

            model_name = model_name or info.get("name", "model")
            logger.info(f"Processing: {model_name}")

            # Get download URL
            download_url = self.get_model_download_url(model_id)
            if not download_url:
                logger.error(f"No download URL available for {model_name}")
                return None

            # Download
            filepath = self.download_model(download_url, model_name)
            if not filepath:
                return None

            # Convert to STL
            if not ModelConverter.is_supported(filepath, "input"):
                logger.error(f"Unsupported format: {filepath.suffix}")
                return None

            stl_path = ModelConverter.to_stl(filepath, output_path=self.output_dir / f"{model_name}.stl")
            logger.success(f"Saved: {stl_path}")

            return stl_path

        except Exception as e:
            logger.error(f"Download and convert failed: {e}")
            return None

    def close(self):
        """Close API client connection."""
        self.api_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()


class WoWHeadScraper:
    """
    Scraper for WoWHead dressing room models.
    
    NOTE: Requires Playwright and careful license verification.
    """

    def __init__(self):
        """
        Initialize WoWHead scraper.
        
        Requires: pip install playwright && playwright install chromium
        """
        config = get_config()
        self.download_dir = Path(config.download_dir)
        self.output_dir = Path(config.output_dir)
        self.converter = ModelConverter()
        self._playwright = None
        self._browser = None
        self._context = None

        logger.info("WoWHead scraper initialized (requires Playwright)")

    async def _init_browser(self):
        """
        Initialize Playwright browser (async).
        """
        try:
            from playwright.async_api import async_playwright

            config = get_config()
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=config.wowhead_headless
            )
            self._context = await self._browser.new_context()

            logger.debug("Playwright browser initialized")

        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            raise

    def get_character_models(self, character_link: str) -> List[str]:
        """
        Extract 3D model URLs from a WoWHead character dressing room link.
        
        This is a placeholder for future implementation.
        Requires careful rendering and DOM inspection.

        Args:
            character_link: WoWHead dressing room URL

        Returns:
            List of model URLs
        """
        logger.warning("WoWHead scraper not yet fully implemented")
        logger.info(f"Character link: {character_link}")
        return []

    def close(self):
        """Close browser connections."""
        logger.debug("Closing WoWHead scraper")
        # Cleanup would happen here in async context

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
