"""
Strategy management tools for MarketMaya MCP server.

These tools provide the MCP interface for creating and managing trading strategies.
"""

from typing import Literal, Optional, List
from fastmcp import FastMCP

# Initialize MCP from the parent module
from ..server import mcp
from ..config import API_BASE_URL, get_auth_headers
from ..services import StrategyService


# Initialize service
def _get_service() -> StrategyService:
    """Get strategy service instance."""
    return StrategyService(API_BASE_URL, get_auth_headers())


@mcp.tool()
def create_scalping_strategy(
    strategy_name: str,
    symbol: str,
    exchange: Literal["NSE", "MCX", "BSE"] = "NSE",
    segment: Literal["EQ", "FUT", "OPT"] = "EQ",
    contract: Literal["NEAR", "NEXT", "FAR"] = "NEAR",
    expiry: Literal["MONTHLY", "WEEKLY"] = "MONTHLY",
    averaging_points: int = 100,
    avg_points: Optional[int] = None,  # Alias for averaging_points
    target_points: int = 100,
    max_steps: int = 50,
    quantity: int = 1,
    lot: int = 1,
    side: Literal["BUY", "SELL"] = "BUY",
    is_intraday: bool = True,
    intraday_entry_time: str = "9:16",
    intraday_exit_time: str = "15:25",
    required_margin: int = 100000,
    product_type: Literal["NRML", "MIS", "CNC"] = "NRML",
    order_type: Literal["Market Order", "Limit Order"] = "Market Order",
    # Price range settings
    jobbing_start_price: float = 0,
    jobbing_end_price: float = 0,
    # Averaging settings
    average_by: Literal["Point", "Percent"] = "Point",
    target_by: Literal["Point", "Percent"] = "Point",
    maximum_target_steps: int = 0,
    sqroff_on_maximum_steps: bool = False,
    calculate_qty_on_market_jump: bool = False,
    # Quantity increase settings
    increase_qty_on_avg: bool = False,
    increase_qty: int = 0,
    increase_qty_type: Literal["Qty", "Lot"] = "Qty",
    scalping_opening_qty: int = 0,
    # Limit order settings
    no_of_limit_order_retry: int = 0,
    retry_at_every_seconds: int = 0,
    market_order_after_retry: bool = False,
    # Rollover settings
    is_auto_rollover: bool = False,
    rollover_before_days: int = 0,
    rollover_time: str = "0:0",
    # Master TP/SL settings
    reset_cycle_by_master_tpsl: bool = False,
    master_tp_money: int = 0,
    master_sl_money: int = 0,
    reset_cycle_on_positive_mtm: int = 0,
    # Trail SL settings
    is_trail_sl: bool = False,
    profit_move: int = 0,
    sl_move: int = 0,
    no_of_trail_sl: int = 0,
    # Options settings
    atm: int = 0,
    strike_price: int = 0,
    option_type: Literal["CE", "PE"] = "CE",
    # Other settings
    allow_update_parameters: bool = True,
    is_add_hedge_leg: bool = False,
) -> dict:
    """
    Create and deploy a scalping strategy to MarketMaya.

    Args:
        strategy_name: Name of the strategy (e.g., "RELIANCE Scalping")
        symbol: Trading symbol (e.g., RELIANCE, SILVER, NIFTY)
        exchange: Exchange - NSE, MCX, or BSE (default: NSE)
        segment: Market segment - EQ (Equity), FUT (Futures), OPT (Options) (default: EQ)
        contract: Contract type for FUT/OPT - NEAR, NEXT, FAR (default: NEAR)
        expiry: Expiry type for FUT/OPT - MONTHLY or WEEKLY (default: MONTHLY)
        averaging_points: Points interval for averaging down (default: 100)
        target_points: Target profit in points (default: 100)
        max_steps: Maximum number of averaging steps (default: 50)
        quantity: Quantity per trade (default: 1)
        lot: Lot size multiplier (default: 1)
        side: Trade direction - BUY or SELL (default: BUY)
        is_intraday: Whether this is an intraday strategy (default: True)
        intraday_entry_time: Entry time for intraday in HH:MM format (default: "9:16")
        intraday_exit_time: Exit time for intraday in HH:MM format (default: "15:25")
        required_margin: Required margin for the strategy (default: 100000)
        product_type: Product type - NRML, MIS, CNC (default: NRML)
        order_type: Order type - Market Order or Limit Order (default: Market Order)
        ... (other optional parameters)

    Returns:
        API response with strategy ID and deployment status
    """
    # Handle alias for averaging_points
    if avg_points is not None:
        averaging_points = avg_points
    
    # Collect all optional parameters
    kwargs = {
        "jobbing_start_price": jobbing_start_price,
        "jobbing_end_price": jobbing_end_price,
        "average_by": average_by,
        "target_by": target_by,
        "maximum_target_steps": maximum_target_steps,
        "sqroff_on_maximum_steps": sqroff_on_maximum_steps,
        "calculate_qty_on_market_jump": calculate_qty_on_market_jump,
        "increase_qty_on_avg": increase_qty_on_avg,
        "increase_qty": increase_qty,
        "increase_qty_type": increase_qty_type,
        "scalping_opening_qty": scalping_opening_qty,
        "no_of_limit_order_retry": no_of_limit_order_retry,
        "retry_at_every_seconds": retry_at_every_seconds,
        "market_order_after_retry": market_order_after_retry,
        "is_auto_rollover": is_auto_rollover,
        "rollover_before_days": rollover_before_days,
        "rollover_time": rollover_time,
        "reset_cycle_by_master_tpsl": reset_cycle_by_master_tpsl,
        "master_tp_money": master_tp_money,
        "master_sl_money": master_sl_money,
        "reset_cycle_on_positive_mtm": reset_cycle_on_positive_mtm,
        "is_trail_sl": is_trail_sl,
        "profit_move": profit_move,
        "sl_move": sl_move,
        "no_of_trail_sl": no_of_trail_sl,
        "atm": atm,
        "strike_price": strike_price,
        "option_type": option_type,
        "allow_update_parameters": allow_update_parameters,
        "is_add_hedge_leg": is_add_hedge_leg,
    }
    
    service = _get_service()
    return service.create_scalping_strategy(
        strategy_name=strategy_name,
        symbol=symbol,
        exchange=exchange,
        segment=segment,
        contract=contract,
        expiry=expiry,
        averaging_points=averaging_points,
        target_points=target_points,
        max_steps=max_steps,
        quantity=quantity,
        lot=lot,
        side=side,
        is_intraday=is_intraday,
        intraday_entry_time=intraday_entry_time,
        intraday_exit_time=intraday_exit_time,
        required_margin=required_margin,
        product_type=product_type,
        order_type=order_type,
        **kwargs
    )


@mcp.tool()
def get_my_strategies(
    skip: int = 0,
    take: int = 10,
    search: str = "",
    symbols: Optional[List[str]] = None,
    trading_type: Literal["All", "INTRADAY", "POSITIONAL"] = "All",
    sort_by: Literal["newest", "oldest", "name"] = "newest",
) -> dict:
    """
    Get list of user's trading strategies from MarketMaya.

    Args:
        skip: Number of strategies to skip for pagination (default: 0)
        take: Number of strategies to fetch (default: 10)
        search: Search term to filter strategies by name (default: "")
        symbols: List of symbols to filter by (default: None for all)
        trading_type: Filter by trading type - All, INTRADAY, POSITIONAL (default: All)
        sort_by: Sort order - newest, oldest, name (default: newest)

    Returns:
        List of strategies with their details
    """
    service = _get_service()
    return service.get_my_strategies(
        skip=skip,
        take=take,
        search=search,
        symbols=symbols,
        trading_type=trading_type,
        sort_by=sort_by,
    )


@mcp.tool()
def modify_strategy(
    strategy_id: str,
    strategy_name: Optional[str] = None,
    averaging_points: Optional[int] = None,
    target_points: Optional[int] = None,
    max_steps: Optional[int] = None,
    quantity: Optional[int] = None,
    lot: Optional[int] = None,
    side: Optional[Literal["BUY", "SELL"]] = None,
    is_intraday: Optional[bool] = None,
    intraday_entry_time: Optional[str] = None,
    intraday_exit_time: Optional[str] = None,
    required_margin: Optional[int] = None,
    product_type: Optional[Literal["NRML", "MIS", "CNC"]] = None,
    order_type: Optional[Literal["Market Order", "Limit Order"]] = None,
    jobbing_start_price: Optional[float] = None,
    jobbing_end_price: Optional[float] = None,
    master_tp_money: Optional[int] = None,
    master_sl_money: Optional[int] = None,
    is_trail_sl: Optional[bool] = None,
    profit_move: Optional[int] = None,
    sl_move: Optional[int] = None,
    no_of_trail_sl: Optional[int] = None,
) -> dict:
    """
    Modify an existing scalping strategy on MarketMaya.

    This tool first checks if the strategy can be edited, then updates it with the new parameters.

    Args:
        strategy_id: The encrypted ID of the strategy to modify (get from get_my_strategies)
        strategy_name: New name for the strategy (optional)
        averaging_points: New points interval for averaging (optional)
        target_points: New target profit in points (optional)
        max_steps: New maximum averaging steps (optional)
        quantity: New quantity per trade (optional)
        lot: New lot size multiplier (optional)
        side: New trade direction - BUY or SELL (optional)
        is_intraday: Whether strategy is intraday (optional)
        intraday_entry_time: New entry time HH:MM (optional)
        intraday_exit_time: New exit time HH:MM (optional)
        required_margin: New required margin (optional)
        product_type: New product type - NRML, MIS, CNC (optional)
        order_type: New order type (optional)
        jobbing_start_price: New start price range (optional)
        jobbing_end_price: New end price range (optional)
        master_tp_money: New master take profit (optional)
        master_sl_money: New master stop loss (optional)
        is_trail_sl: Enable/disable trailing SL (optional)
        profit_move: New profit trigger points (optional)
        sl_move: New SL move points (optional)
        no_of_trail_sl: New number of trail SL moves (optional)

    Returns:
        API response with update status
    """
    # Build updates dictionary with only provided values
    updates = {}
    
    field_mapping = {
        "strategy_name": strategy_name,
        "average_value": averaging_points,
        "intraday_target": target_points,
        "maximum_steps": max_steps,
        "qty": quantity,
        "lot": lot,
        "jobbing_side": side,
        "is_intraday": is_intraday,
        "intraday_entry_time": intraday_entry_time,
        "intraday_exit_time": intraday_exit_time,
        "required_margin": required_margin,
        "product_type": product_type,
        "order_type": order_type,
        "jobbing_start_price": jobbing_start_price,
        "jobbing_end_price": jobbing_end_price,
        "master_tp_money": master_tp_money,
        "master_sl_money": master_sl_money,
        "is_trail_sl": is_trail_sl,
        "profit_move": profit_move,
        "sl_move": sl_move,
        "no_of_trail_sl": no_of_trail_sl,
    }
    
    for api_field, value in field_mapping.items():
        if value is not None:
            updates[api_field] = value
    
    service = _get_service()
    return service.modify_strategy(
        strategy_id=strategy_id,
        updates=updates,
        source="MCP"
    )
