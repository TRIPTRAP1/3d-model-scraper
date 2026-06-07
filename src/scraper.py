"""Main scraper classes for Sketchfab and WoWHead."""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

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
    
    Supports extracting 3D models from WoWHead character links and converting to STL.
    """

    def __init__(self, headless: bool = True):
        """
        Initialize WoWHead scraper.
        
        Args:
            headless: Run browser in headless mode (default True)
            
        Requires: pip install playwright && playwright install chromium
        """
        config = get_config()
        self.download_dir = Path(config.download_dir)
        self.output_dir = Path(config.output_dir)
        self.converter = ModelConverter()
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._loop = None

        logger.info("WoWHead scraper initialized")

    async def _init_browser_async(self) -> None:
        """
        Initialize Playwright browser (async).
        """
        try:
            from playwright.async_api import async_playwright

            config = get_config()
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless
            )
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self._page = await self._context.new_page()

            logger.debug("Playwright browser initialized")

        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            raise

    def _init_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Get or create event loop for async operations.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    async def _extract_model_urls_async(self, page_url: str) -> List[str]:
        """
        Extract 3D model URLs from WoWHead dressing room (async).
        
        Args:
            page_url: WoWHead dressing room URL
            
        Returns:
            List of model URLs
        """
        try:
            logger.info(f"Loading WoWHead page: {page_url}")
            
            # Navigate to page
            await self._page.goto(page_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # Wait for 3D viewer to load
            
            # Try multiple strategies to find model URLs
            model_urls = []
            
            # Strategy 1: Look for data-src attributes in img/object tags
            logger.debug("Strategy 1: Searching for data-src attributes...")
            images = await self._page.query_selector_all("[data-src]")
            for img in images:
                src = await img.get_attribute("data-src")
                if src and any(ext in src.lower() for ext in [".glb", ".gltf", ".obj", ".m2"]):
                    model_urls.append(src)
                    logger.debug(f"Found model URL: {src}")
            
            # Strategy 2: Extract from canvas/WebGL content
            logger.debug("Strategy 2: Searching for canvas-related URLs...")
            script_content = await self._page.content()
            
            # Look for common CDN patterns for WoW models
            cdn_patterns = [
                r'https://[\w.-]*blizzard[\w.]*\.com[^\s"<>]+?\.(?:m2|glb|gltf|obj)',
                r'https://render\.worldofwarcraft\.com[^\s"<>]+',
                r'"url"\s*:\s*"([^"]*\.(?:m2|glb|gltf|obj))',
            ]
            
            for pattern in cdn_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    url = match[0] if isinstance(match, tuple) else match
                    if url not in model_urls and url.startswith("http"):
                        model_urls.append(url)
                        logger.debug(f"Found model URL via pattern: {url}")
            
            # Strategy 3: Check JSON data embedded in page
            logger.debug("Strategy 3: Searching for embedded JSON data...")
            json_patterns = re.findall(r'<script[^>]*type="application/json"[^>]*>([^<]+)</script>', script_content)
            for json_str in json_patterns:
                try:
                    data = json.loads(json_str)
                    urls = self._extract_urls_from_dict(data)
                    for url in urls:
                        if url not in model_urls and any(ext in url.lower() for ext in [".glb", ".gltf", ".obj", ".m2"]):
                            model_urls.append(url)
                            logger.debug(f"Found model URL in JSON: {url}")
                except json.JSONDecodeError:
                    continue
            
            logger.info(f"Extracted {len(model_urls)} model URLs")
            return model_urls
            
        except Exception as e:
            logger.error(f"Failed to extract model URLs: {e}")
            return []

    def _extract_urls_from_dict(self, data: Dict, depth: int = 0, max_depth: int = 10) -> List[str]:
        """
        Recursively extract URLs from nested dictionaries.
        
        Args:
            data: Dictionary to search
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            List of URLs found
        """
        urls = []
        
        if depth > max_depth:
            return urls
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    if value.startswith("http") and any(
                        ext in value.lower() for ext in [".glb", ".gltf", ".obj", ".m2", ".png", ".jpg"]
                    ):
                        urls.append(value)
                elif isinstance(value, (dict, list)):
                    urls.extend(self._extract_urls_from_dict(value, depth + 1, max_depth))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    if item.startswith("http") and any(
                        ext in item.lower() for ext in [".glb", ".gltf", ".obj", ".m2", ".png", ".jpg"]
                    ):
                        urls.append(item)
                elif isinstance(item, (dict, list)):
                    urls.extend(self._extract_urls_from_dict(item, depth + 1, max_depth))
        
        return urls

    def extract_model_urls(self, page_url: str) -> List[str]:
        """
        Extract 3D model URLs from WoWHead dressing room.
        
        Args:
            page_url: WoWHead dressing room URL
            
        Returns:
            List of model URLs
        """
        try:
            # Ensure event loop exists
            loop = self._init_event_loop()
            
            # Initialize browser if needed
            if not self._page:
                loop.run_until_complete(self._init_browser_async())
            
            # Extract URLs
            return loop.run_until_complete(self._extract_model_urls_async(page_url))
            
        except Exception as e:
            logger.error(f"Failed to extract model URLs: {e}")
            return []

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
            # Add .m2 extension if needed (WoW model format)
            if not any(download_url.endswith(ext) for ext in [".glb", ".gltf", ".obj", ".m2", ".zip"]):
                if ".m2" in download_url:
                    # Already has m2 in it, just need extension
                    model_name = f"{model_name}.m2"
            
            filename = sanitize_filename(model_name)
            filepath = self.download_dir / filename
            
            logger.info(f"Downloading: {download_url}")
            
            # Use APIClient for downloading
            api_client = APIClient()
            api_client.download(download_url, str(filepath))
            
            logger.success(f"Downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def download_and_convert(
        self,
        model_url: str,
        model_name: str = "wowhead_model",
    ) -> Optional[Path]:
        """
        Download a WoWHead model and convert to STL.
        
        Args:
            model_url: URL of model to download
            model_name: Name for the model
            
        Returns:
            Path to converted STL file or None if failed
        """
        try:
            logger.info(f"Processing WoWHead model: {model_name}")
            
            # Download the model
            filepath = self.download_model(model_url, model_name)
            if not filepath:
                logger.error("Failed to download model")
                return None
            
            logger.debug(f"Downloaded to: {filepath}")
            
            # Check if file is supported format
            if filepath.suffix.lower() in [".m2", ".zip"]:
                logger.warning(
                    f"File format {filepath.suffix} requires special handling. "
                    f"You may need to use WoW model viewers or converters."
                )
                logger.info(f"File saved at: {filepath}")
                return filepath
            
            # Convert to STL if it's a supported format
            if not ModelConverter.is_supported(filepath, "input"):
                logger.error(f"Unsupported format: {filepath.suffix}")
                logger.info(f"File saved at: {filepath}")
                return filepath
            
            # Convert to STL
            stl_path = ModelConverter.to_stl(
                filepath,
                output_path=self.output_dir / f"{model_name}.stl"
            )
            logger.success(f"Converted to STL: {stl_path}")
            
            return stl_path
            
        except Exception as e:
            logger.error(f"Download and convert failed: {e}")
            return None

    async def close_async(self) -> None:
        """
        Close browser connections (async).
        """
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.debug("Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

    def close(self):
        """
        Close browser connections.
        """
        try:
            if self._loop and self._page:
                self._loop.run_until_complete(self.close_async())
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
