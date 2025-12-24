"""
Account service for handling account-related API calls to MarketMaya.
"""

from typing import Dict, Any
from .base import BaseAPIService
import logging

logger = logging.getLogger("mcp_server")


class AccountService(BaseAPIService):
    """Service for account-related API operations."""
    
    def get_point_balance(self) -> Dict[str, Any]:
        """
        Get the user's current point balance.
        
        Returns:
            Dictionary containing point_balance, hold_balance, and total balance
        """
        logger.info("Fetching point balance")
        
        response = self.post("/client/v2/getPointBalance", json={})
        
        if response.get("status") == "error":
            return response
        
        return response
