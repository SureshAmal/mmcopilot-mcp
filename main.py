from fastmcp import FastMCP
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
import httpx
import os
import logging
import sys
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tool_loader import fetch_and_register_tools

load_dotenv()

# Setup logging to stderr (so it shows in backend logs)
logging.basicConfig(
    level=logging.INFO,
    format="[MCP] %(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("Trading Strategy MCP")

# API Configuration
API_BASE_URL = "https://api.marketmaya.com/api"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
FETCH_BEARER_TOKEN = os.getenv("FETCH_BEARER_TOKEN", "")

# Optional source field used by some APIs
SOURCE = os.getenv("SOURCE", "MCP")
logger.info(f"MCP Server initialized. API_BASE_URL: {API_BASE_URL}")
logger.info(f"BEARER_TOKEN configured: {'Yes' if BEARER_TOKEN else 'NO - MISSING!'}")


def get_auth_headers() -> dict:
    """Get authorization headers for API calls"""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }


# ============================================================================
# KNOWLEDGE BASE TOOL
# ============================================================================


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Search the MarketMaya knowledge base for relevant documentation and guides.
    Use this tool when the user asks about how to use the platform, API documentation,
    strategy parameters, or general help.

    Args:
        query: The search query (e.g., "how to create a scalping strategy", "API authentication")

    Returns:
        Relevant text chunks from the knowledge base.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    store_name = os.getenv("MMCOPILOT_STORE_NAME")

    if not api_key:
        return "Error: GEMINI_API_KEY not configured in MCP server."

    if not store_name:
        return "Error: Knowledge base not configured (MMCOPILOT_STORE_NAME missing)."

    try:
        client = genai.Client(api_key=api_key, vertexai=False)

        model = "gemini-2.5-flash-lite"

        # Configure the tool
        file_search_tool = types.Tool(
            file_search=types.FileSearch(file_search_store_names=[store_name], top_k=5)
        )

        # Ask the model to retrieve
        response = client.models.generate_content(
            model=model,
            contents=f"Please search the knowledge base for: '{query}' and provide a detailed summary of the relevant information found. If you find code examples, include them.",
            config=types.GenerateContentConfig(
                tools=[file_search_tool],
                temperature=0.1,
            ),
        )

        if response.text:
            return response.text
        else:
            return "No relevant information found in the knowledge base."

    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Error searching knowledge base: {str(e)}"


if __name__ == "__main__":
    # Register dynamic tools from API
    fetch_and_register_tools(mcp, API_BASE_URL, FETCH_BEARER_TOKEN)
    mcp.run()
