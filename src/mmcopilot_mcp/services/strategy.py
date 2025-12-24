"""
Strategy service for handling strategy-related API calls to MarketMaya.

This service encapsulates all strategy-related business logic and API interactions.
"""

from typing import Literal, Optional, List, Dict, Any
from .base import BaseAPIService
import logging

logger = logging.getLogger("mcp_server")


class StrategyService(BaseAPIService):
    """Service for strategy-related API operations."""
    
    def create_scalping_strategy(
        self,
        strategy_name: str,
        symbol: str,
        exchange: str,
        segment: str,
        contract: str,
        expiry: str,
        averaging_points: int,
        target_points: int,
        max_steps: int,
        quantity: int,
        lot: int,
        side: str,
        is_intraday: bool,
        intraday_entry_time: str,
        intraday_exit_time: str,
        required_margin: int,
        product_type: str,
        order_type: str,
        **kwargs  # All other optional parameters
    ) -> Dict[str, Any]:
        """
        Create a scalping strategy via API.
        
        Args:
            strategy_name: Name of the strategy
            symbol: Trading symbol
            exchange: Exchange (NSE, MCX, BSE)
            segment: Market segment (EQ, FUT, OPT)
            ... (all other parameters)
            **kwargs: Additional optional parameters
            
        Returns:
            API response dictionary
        """
        # Build mix_name based on segment
        if segment == "EQ":
            mix_name = f"{symbol} {segment} {exchange}"
        else:
            mix_name = f"{symbol} {segment} {contract} {expiry}"
        
        # Build descriptions
        short_desc = f"{side} {symbol} at every {averaging_points} points"
        long_desc = f"{side} {symbol} at every {averaging_points} points down side and book profit at {target_points} points."
        
        # Create the strategy payload
        payload = {
            "id": "",
            "strategy_name": strategy_name,
            "short_description": short_desc,
            "long_description": long_desc,
            "strategy_id": "YioJhK5IqBULe8fPLMnXaAaC0$aC0$",  # Scalping plugin ID
            "mix_name": mix_name,
            "main_exchange": exchange,
            "main_segment": segment,
            "main_symbol": symbol,
            "main_contract": contract,
            "main_expiry": expiry,
            "product_type": product_type,
            "exit_order_product_type": "",
            "qty_type": "Qty",
            "qty": quantity,
            "lot": lot,
            "intraday_entry_time": intraday_entry_time,
            "intraday_exit_time": intraday_exit_time,
            "is_intraday": is_intraday,
            "jobbing_side": side,
            "average_by": kwargs.get("average_by", "Point"),
            "average_value": averaging_points,
            "target_by": kwargs.get("target_by", "Point"),
            "target": 0,
            "intraday_target": target_points,
            "maximum_steps": max_steps,
            "order_type": order_type,
            "required_margin": required_margin,
            "rebacktest": False,
            "sub": [],
            "effect_all_sub_strategies": False,
        }
        
        # Add all optional parameters from kwargs
        optional_fields = [
            "atm", "strike_price", "option_type", "jobbing_start_price", "jobbing_end_price",
            "maximum_target_steps", "sqroff_on_maximum_steps", "calculate_qty_on_market_jump",
            "allow_update_parameters", "no_of_limit_order_retry", "retry_at_every_seconds",
            "market_order_after_retry", "reset_cycle_by_master_tpsl", "rollover_before_days",
            "is_auto_rollover", "is_add_hedge_leg", "rollover_time", "master_tp_money",
            "master_sl_money", "reset_cycle_on_positive_mtm", "is_trail_sl", "profit_move",
            "sl_move", "no_of_trail_sl", "scalping_opening_qty", "increase_qty_on_avg",
            "increase_qty", "increase_qty_type"
        ]
        
        for field in optional_fields:
            if field in kwargs:
                payload[field] = kwargs[field]
        
        logger.info(f"Creating strategy: {strategy_name} for {symbol}")
        logger.info(f"  Exchange: {exchange}, Segment: {segment}, Side: {side}")
        logger.info(f"  Avg: {averaging_points} pts, Target: {target_points} pts, Max Steps: {max_steps}")
        
        # Make API call
        response = self.post("/mainStrategy/createScalpingStrategy", json=payload)
        
        # Handle response
        if response.get("status") == "error":
            return response
        
        # Handle list response
        if isinstance(response, list):
            logger.info("API returned a list, assuming success")
            strategy_id = "N/A"
            if response and isinstance(response[0], dict):
                strategy_id = response[0].get("id", "N/A")
            
            return {
                "status": "success",
                "message": f"Strategy '{strategy_name}' created successfully!",
                "strategy_id": strategy_id,
                "details": response,
            }
        
        # Check for error in response
        if response.get("error") or response.get("status") == "error":
            error_msg = response.get("message", response.get("error", "Unknown API error"))
            logger.error(f"API returned error: {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
            }
        
        logger.info(f"Strategy created successfully! ID: {response.get('id', 'N/A')}")
        return {
            "status": "success",
            "message": f"Strategy '{strategy_name}' created successfully!",
            "strategy_id": response.get("id", ""),
        }
    
    def get_my_strategies(
        self,
        skip: int = 0,
        take: int = 10,
        search: str = "",
        symbols: Optional[List[str]] = None,
        trading_type: str = "All",
        sort_by: str = "newest",
    ) -> Dict[str, Any]:
        """
        Get list of user's trading strategies.
        
        Args:
            skip: Number to skip for pagination
            take: Number to fetch
            search: Search term
            symbols: List of symbols to filter
            trading_type: Filter by type (All, INTRADAY, POSITIONAL)
            sort_by: Sort order (newest, oldest, name)
            
        Returns:
            Dictionary with strategies list and metadata
        """
        payload = {
            "skip": skip,
            "take": take,
            "search": search,
            "symbols": symbols or [],
            "tradingType": trading_type,
            "strategyMasterIds": [],
            "strategyMaster": {"id": "", "strategy_name": "All Plugins", "selected": True},
            "AuthorIds": [],
            "sortBy": sort_by,
        }
        
        response = self.post("/V3/mainStrategy/getClientMyStrategy", json=payload)
        
        if response.get("status") == "error":
            return response
        
        # Extract relevant data
        strategies = []
        for strategy in response.get("data", []):
            strategies.append({
                "id": strategy.get("id"),
                "sid": strategy.get("sid"),
                "name": strategy.get("strategy_name"),
                "plugin": strategy.get("plugin_name"),
                "symbol": strategy.get("main_symbol"),
                "trading_type": strategy.get("trading_type"),
                "required_margin": strategy.get("required_margin_format"),
                "is_deployed": strategy.get("is_deployed"),
                "created_on": strategy.get("created_on"),
                "type": strategy.get("type"),
            })
        
        return {
            "status": "success",
            "total": response.get("total", 0),
            "strategies": strategies,
            "available_symbols": response.get("symbols", []),
        }
    
    def can_edit_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Check if a strategy can be edited.
        
        Args:
            strategy_id: The encrypted strategy ID
            
        Returns:
            Dictionary with canEdit status
        """
        return self.post("/mainStrategy/canEdit", json={"id": strategy_id})
    
    def get_scalping_record(self, strategy_id: str, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the full scalping strategy record.
        
        Args:
            strategy_id: The encrypted strategy ID
            source: Optional source identifier
            
        Returns:
            Complete strategy record
        """
        payload = {"id": strategy_id}
        if source:
            payload["source"] = source
        
        return self.post("/mainStrategy/getScalpingRecord", json=payload)
    
    def modify_strategy(
        self,
        strategy_id: str,
        updates: Dict[str, Any],
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing strategy.
        
        Args:
            strategy_id: The encrypted strategy ID
            updates: Dictionary of fields to update
            source: Optional source identifier
            
        Returns:
            API response with update status
        """
        logger.info(f"Modifying strategy: {strategy_id}")
        
        # First check if can edit
        can_edit_resp = self.can_edit_strategy(strategy_id)
        
        if can_edit_resp.get("status") == "error":
            return can_edit_resp
        
        if isinstance(can_edit_resp, dict) and (
            can_edit_resp.get("error") or can_edit_resp.get("canEdit") is False
        ):
            return {
                "status": "error",
                "message": can_edit_resp.get("message", "Strategy cannot be edited"),
            }
        
        # Fetch current strategy record
        current = self.get_scalping_record(strategy_id, source)
        
        if current.get("status") == "error" or not isinstance(current, dict):
            logger.warning("Could not fetch full strategy record; using minimal update")
            current = {"id": strategy_id}
        
        # Merge updates into current record
        current.update(updates)
        current["id"] = strategy_id
        
        # Send update
        logger.info(f"Sending update with fields: {list(current.keys())}")
        response = self.post("/mainStrategy/createScalpingStrategy", json=current)
        
        if response.get("status") == "error":
            return response
        
        return {
            "status": "success",
            "message": "Strategy updated successfully",
            "response": response
        }
