import sys
import os
import logging

# Add src to path so we can import the package
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mmcopilot_mcp.server import mcp, logger
from mmcopilot_mcp.config import API_BASE_URL, FETCH_BEARER_TOKEN

# Import tool modules to register them with the mcp instance
# import mmcopilot_mcp.tools.static  # Disabled to prefer dynamic tools
import mmcopilot_mcp.tools.knowledge_base
from mmcopilot_mcp.tools.loader import fetch_and_register_tools

if __name__ == "__main__":
    logger.info("Starting MCP Server...")
    logger.info("Static tool 'search_knowledge_base' is active.")
    
    # Register dynamic tools from API
    # We pass FETCH_BEARER_TOKEN as the token to be used by the generated tools
    fetch_and_register_tools(mcp, API_BASE_URL, FETCH_BEARER_TOKEN)
    
    # Run the server
    mcp.run()
