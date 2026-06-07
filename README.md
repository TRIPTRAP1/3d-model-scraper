# 3D Model Scraper

A Python-based scraper for extracting 3D models from Sketchfab and WoWHead Dressing Room, with automatic conversion to STL format.

## Features

- 🎯 **Sketchfab Integration**: Search and download GLTF/GLB models via public API
- 🎮 **WoWHead Support**: Extract character armor and appearance models from the Dressing Room
- 🔄 **Format Conversion**: Automatically converts GLTF/GLB to STL
- ⚡ **Async Processing**: Concurrent downloads and conversions for speed
- 🔍 **Filtering**: Search by license (CC0, CC-BY, etc.), popularity, and more
- 📊 **Logging**: Comprehensive logging and error handling

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/TRIPTRAP1/3d-model-scraper.git
cd 3d-model-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser drivers (for WoWHead)
python -m playwright install chromium
```

### 2. Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings (optional - API token for authenticated requests)
```

### 3. Basic Usage

#### Search and Download from Sketchfab

```python
from src.scraper import SketchfabScraper

scraper = SketchfabScraper()

# Search for CC0 models
results = scraper.search(
    query="dragon",
    license="cc0",
    downloadable=True,
    limit=5
)

# Download and convert
for model in results:
    stl_path = scraper.download_and_convert(model['url'])
    print(f"Saved: {stl_path}")
```

#### Extract from WoWHead

```python
from src.scraper import WoWHeadScraper

scraper = WoWHeadScraper()

# Extract character appearance
model_urls = scraper.get_character_models(
    character_link="https://www.wowhead.com/dressing-room#..."
)

for url in model_urls:
    stl_path = scraper.download_and_convert(url)
    print(f"Saved: {stl_path}")
```

## Project Structure

```
3d-model-scraper/
├── src/
│   ├── __init__.py
│   ├── scraper.py           # Main scraper classes
│   ├── converters.py        # Format conversion logic
│   ├── config.py            # Configuration management
│   ├── utils.py             # Helper functions
│   └── api_client.py        # HTTP client with retries
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuration Options

Edit `.env` to customize:

- `SKETCHFAB_API_TOKEN`: Optional token for higher rate limits
- `DOWNLOAD_DIR`: Where to save downloaded models
- `OUTPUT_DIR`: Where to save converted STL files
- `MAX_WORKERS`: Number of concurrent downloads (default: 4)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, etc.)

## Supported Formats

**Input Formats:**
- GLTF (.gltf)
- GLB (.glb, binary GLTF)
- OBJ (.obj)

**Output Format:**
- STL (.stl)

## Important Legal Notes

### Sketchfab
- Always respect model licenses (CC0, CC-BY, etc.)
- Only download models marked as downloadable
- Use the Sketchfab API responsibly (rate limits apply)
- See https://sketchfab.com/search?features=downloadable&licenses=7c23a1ba438d4306920229c12afcb5f9&type=models for CC0 models

### WoWHead
- Verify that model extraction complies with Blizzard's Terms of Service
- Game assets may have copyright/IP restrictions
- Use scraped models for personal/educational purposes only
- Do not redistribute proprietary Blizzard content

## Rate Limiting & Etiquette

- Default delay between requests: 1 second (configurable)
- Respect `Retry-After` headers
- Use appropriate User-Agent headers
- Don't hammer servers with concurrent requests

## Troubleshooting

### "429 Too Many Requests"
Increase delay in config or use API token for higher limits

### "Model not downloadable"
Some Sketchfab models require authentication. Set `SKETCHFAB_API_TOKEN`

### WoWHead extraction fails
Ensure Playwright browser drivers are installed:
```bash
python -m playwright install chromium
```

## Contributing

Contributions welcome! Areas for improvement:
- Additional format support (FBX, DAE, etc.)
- Better mesh optimization
- Texture preservation
- Performance improvements

## License

MIT License - See LICENSE file (when added)

## Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Respecting intellectual property rights
- Following each source's terms of service
- Ensuring appropriate use of downloaded models
