"""Utility functions for the 3D model scraper."""

import hashlib
import mimetypes
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote

from loguru import logger


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename to be safe for file systems.

    Args:
        filename: The filename to sanitize
        max_length: Maximum filename length (default 200)

    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    invalid_chars = r'<>:"|?*\x00'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Truncate if too long (leave room for extension)
    if len(filename) > max_length:
        base = Path(filename).stem
        ext = Path(filename).suffix
        base = base[: max_length - len(ext) - 1]
        filename = f"{base}{ext}"

    return filename or "model"


def extract_filename_from_url(url: str, fallback: str = "model") -> str:
    """
    Extract a reasonable filename from a URL.

    Args:
        url: The URL to extract filename from
        fallback: Fallback name if extraction fails

    Returns:
        Extracted filename
    """
    try:
        parsed = urlparse(url)
        filename = unquote(Path(parsed.path).name)
        if filename:
            return sanitize_filename(filename)
    except Exception as e:
        logger.warning(f"Failed to extract filename from URL: {e}")

    return fallback


def get_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm (default sha256)

    Returns:
        Hex hash string
    """
    hash_obj = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def get_mime_type(filepath: Path) -> str:
    """
    Get MIME type of a file.

    Args:
        filepath: Path to the file

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(filepath))
    return mime_type or "application/octet-stream"


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_size(filepath: Path) -> int:
    """
    Get file size in bytes.

    Args:
        filepath: Path to the file

    Returns:
        File size in bytes
    """
    return filepath.stat().st_size if filepath.exists() else 0
