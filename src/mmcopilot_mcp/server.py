"""
MMCopilot MCP Server

This is the main entry point for the MCP server that provides trading tools
for MarketMaya platform.
"""

import logging
import sys
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[MCP] %(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("mcp_server")

# Reduce verbosity of httpx HTTP request logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Initialize MCP server
mcp = FastMCP("Trading Strategy MCP")

logger.info("=" * 60)
logger.info("Initializing MMCopilot MCP Server")
logger.info("=" * 60)

# Import and register all static tools
try:
    from .tools import register_all_static_tools
    register_all_static_tools()
    logger.info("✅ Static tools registered")
except Exception as e:
    logger.error(f"❌ Failed to register static tools: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Import and register dynamic tools
try:
    from .config import API_BASE_URL, BEARER_TOKEN
    from .tools.loader import fetch_and_register_tools
    
    logger.info("Attempting to load dynamic tools...")
    fetch_and_register_tools(mcp, API_BASE_URL, BEARER_TOKEN)
    logger.info("✅ Dynamic tool loading complete")
except Exception as e:
    logger.error(f"⚠️  Dynamic tool loading failed (server will continue): {e}")
    import traceback
    logger.error(traceback.format_exc())

logger.info("=" * 60)
logger.info("MMCopilot MCP Server initialized successfully")
logger.info("=" * 60)
