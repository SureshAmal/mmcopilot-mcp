import os
import json
import logging
from google import genai
from google.genai import types
from ..server import mcp, logger
from ..config import GEMINI_API_KEY, STORE_CONFIG_FILE, FETCH_BEARER_TOKEN
from ..scripts import sync_kb

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
    logger.info(f"Executing search_knowledge_base with query: {query}")
    api_key = GEMINI_API_KEY
    
    # Try to load store name from config file first, then env var
    store_name = os.getenv("MMCOPILOT_STORE_NAME")
    
    if os.path.exists(STORE_CONFIG_FILE):
        try:
            with open(STORE_CONFIG_FILE, "r") as f:
                config = json.load(f)
                if config.get("store_name"):
                    store_name = config.get("store_name")
                    logger.info(f"Loaded store name from config: {store_name}")
        except Exception as e:
            logger.error(f"Failed to load store config: {e}")

    if not api_key:
        return "Error: GEMINI_API_KEY not configured in MCP server."

    if not store_name:
        logger.info("Store name not found. Attempting to auto-create knowledge base...")
        try:
            if not FETCH_BEARER_TOKEN:
                 return "Error: Knowledge base not configured and FETCH_BEARER_TOKEN missing. Cannot auto-create."
            
            docs = sync_kb.fetch_documents_from_api()
            if docs:
                store_name = sync_kb.upload_to_gemini(docs)
                if store_name:
                    logger.info(f"Auto-created new store: {store_name}")
                    # sync_kb saves to file, so next time it will load from config
                    
                    # Update config file immediately if possible (sync_kb does it)
                    config = {"store_name": store_name, "last_synced": 0} # timestamp not critical here
                    with open(STORE_CONFIG_FILE, "w") as f:
                        json.dump(config, f, indent=2)
                else:
                    return "Error: Failed to create knowledge base (upload failed)."
            else:
                return "Error: Failed to fetch documents for knowledge base."
        except Exception as e:
            logger.error(f"Auto-creation failed: {e}")
            return f"Error: Knowledge base not configured and auto-creation failed: {e}"

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
                system_instruction="You retrive information from the knowledge base to help the user. Provide detailed and helpful answers based on the documents you find. and if not found say no relevant information found.",
            ),
        )

        if response.text:
            return response.text
        else:
            return "No relevant information found in the knowledge base."

    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Error searching knowledge base: {str(e)}"
