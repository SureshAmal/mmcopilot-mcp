import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (3 levels up from this file)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Debug: Print env path and status
import sys
print(f"🔍 Loading .env from: {env_path}", file=sys.stderr)
print(f"🔍 .env exists: {env_path.exists()}", file=sys.stderr)
if env_path.exists():
    print(f"🔍 .env size: {env_path.stat().st_size} bytes", file=sys.stderr)

# API Configuration
API_BASE_URL = "https://api.marketmaya.com/api"
WEBAPI_BASE_URL = "https://webapi.marketmaya.com/api"

# Auth
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
FETCH_BEARER_TOKEN = os.getenv("FETCH_BEARER_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Source
SOURCE = os.getenv("SOURCE", "MCP")

# Store Config
STORE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "store_config.json")

def get_auth_headers() -> dict:
    """Get authorization headers for API calls"""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }
