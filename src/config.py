"""Configuration management for the 3D model scraper."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration loaded from .env file."""

    # Sketchfab API
    sketchfab_api_token: Optional[str] = Field(default=None, env="SKETCHFAB_API_TOKEN")
    sketchfab_api_url: str = Field(
        default="https://api.sketchfab.com/v3",
        env="SKETCHFAB_API_URL"
    )

    # Download settings
    download_dir: str = Field(default="./downloads", env="DOWNLOAD_DIR")
    output_dir: str = Field(default="./outputs", env="OUTPUT_DIR")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")

    # WoWHead settings
    wowhead_headless: bool = Field(default=True, env="WOWHEAD_HEADLESS")
    wowhead_timeout: int = Field(default=30000, env="WOWHEAD_TIMEOUT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @validator("max_workers")
    def validate_max_workers(cls, v):
        """Validate max_workers is reasonable."""
        if not 1 <= v <= 32:
            raise ValueError("max_workers must be between 1 and 32")
        return v

    def __init__(self, **data):
        """Initialize config and create necessary directories."""
        # Load .env if it exists
        if Path(".env").exists():
            load_dotenv(".env")

        super().__init__(**data)

        # Create directories if they don't exist
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


def get_config() -> Config:
    """Get or create the global config instance."""
    if not hasattr(get_config, "_instance"):
        get_config._instance = Config()
    return get_config._instance
