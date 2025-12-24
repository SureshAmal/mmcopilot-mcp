"""
Backtest tools for MarketMaya MCP server.
"""

from ..server import mcp
from ..config import API_BASE_URL, get_auth_headers
from ..services import BacktestService


def _get_service() -> BacktestService:
    """Get backtest service instance."""
    return BacktestService(API_BASE_URL, get_auth_headers())


@mcp.tool()
def get_backtest_options(strategy_id: str) -> dict:
    """
    Get backtest options for a specific strategy.

    Args:
        strategy_id: The encrypted ID of the strategy (e.g., "mdaB0$Eix..."). NOT the simple numeric ID.

    Returns:
        Dictionary containing available backtest options.
    """
    service = _get_service()
    return service.get_backtest_options(strategy_id)
