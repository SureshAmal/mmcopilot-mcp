"""
Tools package for mmcopilot-mcp.

This package contains all MCP tools organized by functionality.
"""

def register_all_static_tools():
    """
    Register all static tools with the MCP server.
    
    Import will auto-register via @mcp.tool() decorators.
    """
    # Only import knowledge_base - other tools will come from dynamic loading
    from . import knowledge_base
    
    # Tools are automatically registered via decorators
    # No need to return anything


# Public API
__all__ = [
    "register_all_static_tools",
]