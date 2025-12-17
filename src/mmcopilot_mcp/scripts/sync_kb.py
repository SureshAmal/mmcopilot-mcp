import os
import json
import httpx
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import tempfile
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration
# If run as script, we might need to adjust paths or imports
if __name__ == "__main__":
    # Add src to path if running directly
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from mmcopilot_mcp.config import FETCH_BEARER_TOKEN, GEMINI_API_KEY, STORE_CONFIG_FILE, WEBAPI_BASE_URL
else:
    from ..config import FETCH_BEARER_TOKEN, GEMINI_API_KEY, STORE_CONFIG_FILE, WEBAPI_BASE_URL

API_URL = f"{WEBAPI_BASE_URL}/AiDocumentMaster/GetAIDocList"

def fetch_documents_from_api():
    """Fetch documents from MarketMaya API"""
    print(f"📥 Fetching documents from {API_URL}...")
    
    params = {
        "Skip": 0,
        "Take": 100,  # Fetch up to 100 docs
        "OrderBy": "entryDateTime",
        "Filter": "",
        "OrderDirection": 1,
        "ColumnFilters": "{}",
        "wlId": "undefined"
    }
    
    headers = {
        "Authorization": f"Bearer {FETCH_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract docs list
            if "data" in data and "aiDocs" in data["data"]:
                docs = data["data"]["aiDocs"]
                print(f"✅ Found {len(docs)} documents.")
                return docs
            else:
                print("⚠️ Unexpected API response structure.")
                print(json.dumps(data, indent=2))
                return []
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        return []

def upload_to_gemini(docs):
    """Upload documents to Google Gemini and create a Vector Store"""
    if not docs:
        print("No documents to upload.")
        return None

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment variables.")
        return None

    print("🚀 Initializing Gemini Client...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    uploaded_files = []
    
    # Create a temporary directory to store files before uploading
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 Created temp directory: {temp_dir}")
        
        for doc in docs:
            title = doc.get("documentTitle", "Untitled")
            content = doc.get("documentContent", "")
            doc_id = doc.get("id", "unknown")
            
            if not content:
                print(f"⚠️ Skipping '{title}' (empty content)")
                continue
                
            # Sanitize filename
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            filename = f"{safe_title}_{doc_id[:8]}.txt"
            file_path = os.path.join(temp_dir, filename)
            
            # Write content to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n")
                f.write(f"Remark: {doc.get('documentRemark', '')}\n")
                f.write("-" * 20 + "\n")
                f.write(content)
            
            print(f"Tb Uploading '{filename}' to Gemini...")
            try:
                # Upload file
                # For google-genai package (v0.3+):
                with open(file_path, "rb") as f:
                    file_obj = client.files.upload(file=f, config=types.UploadFileConfig(display_name=title, mime_type="text/plain"))
                
                print(f"   ✅ Uploaded: {file_obj.name}")
                uploaded_files.append(file_obj)
                
                # Small delay to avoid rate limits
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Failed to upload '{filename}': {e}")

    if not uploaded_files:
        print("❌ No files were successfully uploaded.")
        return None

    # Create Vector Store (File Search Store)
    store_name = f"MarketMaya_KB_{int(time.time())}"
    print(f"📦 Creating File Search Store: {store_name}...")
    
    try:
        # Create store
        # Using google-genai v0.3+ syntax
        if hasattr(client, "file_search_stores"):
            store_client = client.file_search_stores
            config_type = types.CreateFileSearchStoreConfig
        elif hasattr(client, "vector_stores"):
            store_client = client.vector_stores
            config_type = types.CreateVectorStoreConfig
        else:
            print("❌ Client does not support file_search_stores or vector_stores.")
            return None

        vector_store = store_client.create(
            config=config_type(
                display_name=f"MarketMaya Knowledge Base (Synced {time.strftime('%Y-%m-%d %H:%M')})"
            )
        )
        
        print(f"   ✅ Created Store: {vector_store.name}")
        
        # Add files to store
        file_ids = [f.name for f in uploaded_files]
        print(f"   🔗 Adding {len(file_ids)} files to store...")
        
        # Try to add files
        # If import_file exists, use it (one by one?)
        if hasattr(store_client, "import_file"):
            for file_id in file_ids:
                try:
                    # import_file(file_search_store_name=..., file_name=...)
                    store_client.import_file(file_search_store_name=vector_store.name, file_name=file_id)
                except Exception as e:
                    print(f"      ⚠️ Failed to import {file_id}: {e}")
        else:
            print("      ⚠️ No import_file method found. Files might not be linked.")

    except Exception as e:
        print(f"❌ Error creating/populating store: {e}")
        return None

    return vector_store.name

def main():
    print("=== MarketMaya Knowledge Base Sync ===")
    
    # 1. Fetch
    docs = fetch_documents_from_api()
    if not docs:
        print("No documents found. Exiting.")
        return

    # 2. Upload & Create Store
    store_name = upload_to_gemini(docs)
    
    if store_name:
        print(f"\n✅ Sync Complete!")
        print(f"🆔 New Vector Store Name: {store_name}")
        
        # 3. Save to config
        config = {"store_name": store_name, "last_synced": time.time()}
        with open(STORE_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"💾 Saved configuration to {STORE_CONFIG_FILE}")
        print("👉 The MCP server will use this store on next restart.")
    else:
        print("\n❌ Sync Failed.")

if __name__ == "__main__":
    main()
