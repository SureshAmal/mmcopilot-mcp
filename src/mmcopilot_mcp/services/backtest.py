"""
Backtest service for handling backtest-related API calls to MarketMaya.
"""

from typing import Dict, Any
from .base import BaseAPIService
import logging

logger = logging.getLogger("mcp_server")


class BacktestService(BaseAPIService):
    """Service for backtest-related API operations."""
    
    def get_backtest_options(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get backtest options for a specific strategy.
        
        Args:
            strategy_id: The encrypted ID of the strategy
            
        Returns:
            Dictionary containing available backtest options
        """
        logger.info(f"Fetching backtest options for strategy: {strategy_id}")
        
        # Ensure ID is clean
        clean_id = str(strategy_id).strip()
        payload = {"id": clean_id}
        
        response = self.post("/subscription/getBacktestOptions", json=payload)
        
        if response.get("status") == "error":
            return response
        
        return response
