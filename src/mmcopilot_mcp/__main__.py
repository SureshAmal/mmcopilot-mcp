"""
Entry point for running the MMCopilot MCP Server.

Run with: python -m mmcopilot_mcp
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (3 levels up from this file)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def validate_environment():
    """Validate required environment variables are set."""
    required_vars = ["BEARER_TOKEN"]
    optional_vars = ["FETCH_BEARER_TOKEN", "GEMINI_API_KEY"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print("❌ Missing required environment variables:", file=sys.stderr)
        for var in missing_required:
            print(f"   - {var}", file=sys.stderr)
        print("\nPlease set these variables in your .env file or environment.", file=sys.stderr)
        return False
    
    if missing_optional:
        print("⚠️  Warning: Optional environment variables not set:", file=sys.stderr)
        for var in missing_optional:
            print(f"   - {var}", file=sys.stderr)
        print("   Some features may be disabled.\n", file=sys.stderr)
    
    return True


def main():
    """Main entry point for the MCP server."""
    print("=" * 70, file=sys.stderr)
    print("MMCopilot MCP Server", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    print("✅ Environment validation passed", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Import and run server
    try:
        from .server import mcp
        print("✅ Server imported successfully", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("Server is ready to accept requests", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        
        # Run the MCP server (FastMCP handles the main loop)
        mcp.run()
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70, file=sys.stderr)
        print("Server shutdown requested", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
