"""HTTP client with retry logic and rate limiting."""

import asyncio
import time
from typing import Any, Dict, Optional

import aiohttp
import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import get_config


class APIClient:
    """HTTP client with retry logic and rate limiting."""

    def __init__(
        self,
        base_url: str = "",
        api_token: Optional[str] = None,
        timeout: int = 30,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL for API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.api_token = api_token
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Setup session with retry logic
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Default headers
        session.headers.update({
            "User-Agent": "3D-Model-Scraper/0.1.0 (+https://github.com/TRIPTRAP1/3d-model-scraper)",
            "Accept": "application/json",
        })

        if self.api_token:
            session.headers.update({"Authorization": f"Bearer {self.api_token}"})

        return session

    def _wait_for_rate_limit(self) -> None:
        """Enforce rate limit delay between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make GET request with rate limiting.

        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            **kwargs: Additional arguments to pass to requests.get()

        Returns:
            Response object
        """
        self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url}")

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def download(
        self,
        url: str,
        filepath: str,
        chunk_size: int = 8192,
    ) -> None:
        """
        Download file with streaming and progress.

        Args:
            url: URL to download from
            filepath: Path to save file
            chunk_size: Download chunk size
        """
        self._wait_for_rate_limit()

        logger.info(f"Downloading: {url} -> {filepath}")

        response = self.session.get(
            url,
            timeout=self.timeout,
            stream=True,
        )
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(filepath, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        logger.debug(f"Progress: {percent:.1f}%")

        logger.info(f"Downloaded: {filepath}")

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
