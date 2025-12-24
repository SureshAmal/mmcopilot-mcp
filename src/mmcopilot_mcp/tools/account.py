"""
Account management tools for MarketMaya MCP server.
"""

from ..server import mcp
from ..config import API_BASE_URL, get_auth_headers
from ..services import AccountService


def _get_service() -> AccountService:
    """Get account service instance."""
    return AccountService(API_BASE_URL, get_auth_headers())


@mcp.tool()
def get_point_balance() -> dict:
    """
    Get the user's current point balance from MarketMaya.

    Returns:
        Dictionary containing point_balance, hold_balance, and total balance
    """
    service = _get_service()
    return service.get_point_balance()
