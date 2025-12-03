# server.py
from fastmcp import FastMCP
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mcp = FastMCP("Trading Strategy MCP")

# API Configuration
API_BASE_URL = "https://api.marketmaya.com/api"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")


def get_auth_headers() -> dict:
    """Get authorization headers for API calls"""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }


# ============================================================================
# SCALPING STRATEGY TOOL
# ============================================================================

@mcp.tool()
def create_scalping_strategy(
    strategy_name: str,
    symbol: str,
    exchange: Literal["NSE", "MCX", "BSE"] = "NSE",
    segment: Literal["EQ", "FUT", "OPT"] = "EQ",
    contract: Literal["NEAR", "NEXT", "FAR"] = "NEAR",
    expiry: Literal["MONTHLY", "WEEKLY"] = "MONTHLY",
    averaging_points: int = 100,
    target_points: int = 100,
    max_steps: int = 50,
    quantity: int = 1,
    lot: int = 1,
    side: Literal["BUY", "SELL"] = "BUY",
    is_intraday: bool = False,
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
        is_intraday: Whether this is an intraday strategy (default: False)
        intraday_entry_time: Entry time for intraday in HH:MM format (default: "9:16")
        intraday_exit_time: Exit time for intraday in HH:MM format (default: "15:25")
        required_margin: Required margin for the strategy (default: 100000)
        product_type: Product type - NRML, MIS, CNC (default: NRML)
        order_type: Order type - Market Order or Limit Order (default: Market Order)
        jobbing_start_price: Start price for price range (default: 0 = no limit)
        jobbing_end_price: End price for price range (default: 0 = no limit)
        average_by: Average calculation method - Point or Percent (default: Point)
        target_by: Target calculation method - Point or Percent (default: Point)
        maximum_target_steps: Max target steps before booking (default: 0)
        sqroff_on_maximum_steps: Square off when max steps reached (default: False)
        calculate_qty_on_market_jump: Adjust qty on market gap (default: False)
        increase_qty_on_avg: Increase quantity on averaging (default: False)
        increase_qty: Amount to increase quantity by (default: 0)
        increase_qty_type: Type for qty increase - Qty or Lot (default: None)
        scalping_opening_qty: Opening quantity for scalping (default: 0)
        no_of_limit_order_retry: Number of limit order retries (default: 0)
        retry_at_every_seconds: Seconds between retries (default: 0)
        market_order_after_retry: Place market order after retry fails (default: False)
        is_auto_rollover: Enable auto rollover for FUT/OPT (default: False)
        rollover_before_days: Days before expiry to rollover (default: 0)
        rollover_time: Time to perform rollover in HH:MM (default: "0:0")
        reset_cycle_by_master_tpsl: Reset cycle on master TP/SL hit (default: False)
        master_tp_money: Master take profit in money (default: 0)
        master_sl_money: Master stop loss in money (default: 0)
        reset_cycle_on_positive_mtm: Reset when MTM reaches this positive value (default: 0)
        is_trail_sl: Enable trailing stop loss (default: False)
        profit_move: Points profit to trigger trail (default: 0)
        sl_move: Points to move SL by (default: 0)
        no_of_trail_sl: Number of trail SL moves (default: 0)
        atm: ATM strike offset for options (default: 0)
        strike_price: Specific strike price for options (default: 0)
        option_type: Option type - CE or PE (default: "")
        allow_update_parameters: Allow parameter updates (default: True)
        is_add_hedge_leg: Add hedge leg to strategy (default: False)

    Returns:
        API response with strategy ID and deployment status
    """
    
    # Build mix_name based on segment
    if segment == "EQ":
        mix_name = f"{symbol} {segment} {exchange}"
    else:
        mix_name = f"{symbol} {segment} {contract} {expiry}"
    
    # Build short and long descriptions
    short_desc = f"{side} {symbol} at every {averaging_points} points"
    long_desc = f"{side} {symbol} at every {averaging_points} points down side and book profit at {target_points} points."
    
    # Create the strategy payload with ALL parameters
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
        "atm": atm,
        "strike_price": strike_price,
        "option_type": option_type,
        "intraday_entry_time": intraday_entry_time,
        "intraday_exit_time": intraday_exit_time,
        "is_intraday": is_intraday,
        "jobbing_side": side,
        "jobbing_start_price": jobbing_start_price,
        "jobbing_end_price": jobbing_end_price,
        "average_by": average_by,
        "average_value": averaging_points,
        "target_by": target_by,
        "target": 0,
        "intraday_target": target_points,
        "maximum_steps": max_steps,
        "maximum_target_steps": maximum_target_steps,
        "sqroff_on_maximum_steps": sqroff_on_maximum_steps,
        "calculate_qty_on_market_jump": calculate_qty_on_market_jump,
        "allow_update_parameters": allow_update_parameters,
        "order_type": order_type,
        "no_of_limit_order_retry": no_of_limit_order_retry,
        "retry_at_every_seconds": retry_at_every_seconds,
        "market_order_after_retry": market_order_after_retry,
        "reset_cycle_by_master_tpsl": reset_cycle_by_master_tpsl,
        "rollover_before_days": rollover_before_days,
        "is_auto_rollover": is_auto_rollover,
        "is_add_hedge_leg": is_add_hedge_leg,
        "rollover_time": rollover_time,
        "master_tp_money": master_tp_money,
        "master_sl_money": master_sl_money,
        "reset_cycle_on_positive_mtm": reset_cycle_on_positive_mtm,
        "required_margin": required_margin,
        "is_trail_sl": is_trail_sl,
        "profit_move": profit_move,
        "sl_move": sl_move,
        "no_of_trail_sl": no_of_trail_sl,
        "scalping_opening_qty": scalping_opening_qty,
        "increase_qty_on_avg": increase_qty_on_avg,
        "increase_qty": increase_qty,
        "increase_qty_type": increase_qty_type,
        "rebacktest": False,
        "sub": [],
        "effect_all_sub_strategies": False,
    }

    # Make API call to create the strategy
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/mainStrategy/createScalpingStrategy",
                headers=get_auth_headers(),
                json=payload,
            )
            response.raise_for_status()
            api_response = response.json()
            
            return {
                "status": "success",
                "message": f"Strategy '{strategy_name}' created successfully!",
                "payload": payload,
                "response": api_response,
            }
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"API error: {e.response.status_code} - {e.response.text}",
            "payload": payload,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create strategy: {str(e)}",
            "payload": payload,
        }


# ============================================================================
# GET MY STRATEGIES TOOL
# ============================================================================

@mcp.tool()
def get_my_strategies(
    skip: int = 0,
    take: int = 10,
    search: str = "",
    symbols: List[str] = None,
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
    
    # Build request payload
    payload = {
        "skip": skip,
        "take": take,
        "search": search,
        "symbols": symbols or [],
        "tradingType": trading_type,
        "strategyMasterIds": [],
        "strategyMaster": {
            "id": "",
            "strategy_name": "All Plugins",
            "selected": True
        },
        "AuthorIds": [],
        "sortBy": sort_by,
    }

    # Make API call
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/V3/mainStrategy/getClientMyStrategy",
                headers=get_auth_headers(),
                json=payload,
            )
            response.raise_for_status()
            api_response = response.json()
            
            # Extract relevant data
            strategies = []
            for strategy in api_response.get("data", []):
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
                "total": api_response.get("total", 0),
                "strategies": strategies,
                "available_symbols": api_response.get("symbols", []),
            }
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"API error: {e.response.status_code} - {e.response.text}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch strategies: {str(e)}",
        }


if __name__ == "__main__":
    mcp.run()
