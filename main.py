# server.py
import logging
import os
import sys
from typing import List, Literal, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

# Setup logging to stderr (so it shows in backend logs)
logging.basicConfig(
    level=logging.INFO,
    format="[MCP] %(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("Trading Strategy MCP")

# API Configuration
API_BASE_URL = "https://api.marketmaya.com/api"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

logger.info(f"MCP Server initialized. API_BASE_URL: {API_BASE_URL}")
logger.info(f"BEARER_TOKEN configured: {'Yes' if BEARER_TOKEN else 'NO - MISSING!'}")


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
        strategy_name: Name of the strategy (e.g., "RELIANCE Scalping") if user did not provide then create appropriate name
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

    # Handle alias for averaging_points
    if avg_points is not None:
        averaging_points = avg_points

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

    logger.info(f"🚀 Creating strategy: {strategy_name} for {symbol}")
    logger.info(f"   Exchange: {exchange}, Segment: {segment}, Side: {side}")
    logger.info(
        f"   Avg: {averaging_points} pts, Target: {target_points} pts, Max Steps: {max_steps}"
    )

    # Make API call to create the strategy
    try:
        logger.info(
            f"📤 Calling API: {API_BASE_URL}/mainStrategy/createScalpingStrategy"
        )
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/mainStrategy/createScalpingStrategy",
                headers=get_auth_headers(),
                json=payload,
            )

            logger.info(f"📥 API Response Status: {response.status_code}")

            # Check for API errors before raising
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "message", error_data.get("error", response.text)
                    )
                except Exception:
                    error_msg = response.text
                logger.error(f"❌ API Error: {error_msg}")
                return {
                    "status": "error",
                    "message": f"API returned error: {error_msg}",
                }

            api_response = response.json()
            logger.info(f"📥 API Response: {api_response}")

            # Handle list response (assume success if list is returned)
            if isinstance(api_response, list):
                logger.info("✅ API returned a list, assuming success.")
                # Try to find an ID in the first element if available
                strategy_id = "N/A"
                if api_response and isinstance(api_response[0], dict):
                    strategy_id = api_response[0].get("id", "N/A")

                return {
                    "status": "success",
                    "message": f"Strategy '{strategy_name}' created successfully!",
                    "strategy_id": strategy_id,
                    "details": api_response,
                }

            # Check if response indicates an error
            if api_response.get("error") or api_response.get("status") == "error":
                error_msg = api_response.get(
                    "message", api_response.get("error", "Unknown API error")
                )
                logger.error(f"❌ API returned error status: {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                }

            logger.info(
                f"✅ Strategy created successfully! ID: {api_response.get('id', 'N/A')}"
            )
            return {
                "status": "success",
                "message": f"Strategy '{strategy_name}' created successfully!",
                "strategy_id": api_response.get("id", ""),
            }
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP Error: {e}")
        try:
            error_data = e.response.json()
            error_msg = error_data.get("message", error_data.get("error", str(e)))
        except Exception:
            error_msg = e.response.text
        logger.error(f"❌ Error message: {error_msg}")
        return {
            "status": "error",
            "message": f"API error: {error_msg}",
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Failed to create strategy: {str(e)}",
        }


# ============================================================================
# GET MY STRATEGIES TOOL
# ============================================================================


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

    # Build request payload
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
                strategies.append(
                    {
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
                    }
                )

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


# ============================================================================
# KNOWLEDGE BASE TOOL
# ============================================================================


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Search the MarketMaya knowledge base for relevant documentation and guides.
    Use this tool when the user asks about how to use the platform, API documentation,
    strategy parameters, or general help.

    Args:
        query: The search query (e.g., "how to create a scalping strategy", "API authentication")

    Returns:
        Relevant text chunks from the knowledge base.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    store_name = os.getenv("MMCOPILOT_STORE_NAME")

    if not api_key:
        return "Error: GEMINI_API_KEY not configured in MCP server."

    if not store_name:
        return "Error: Knowledge base not configured (MMCOPILOT_STORE_NAME missing)."

    try:
        client = genai.Client(api_key=api_key, vertexai=False)

        model = "gemini-2.5-flash-lite"

        # Configure the tool
        file_search_tool = types.Tool(
            file_search=types.FileSearch(file_search_store_names=[store_name], top_k=5)
        )

        # Ask the model to retrieve
        response = client.models.generate_content(
            model=model,
            contents=f"Please search the knowledge base for: '{query}' and provide a detailed summary of the relevant information found. If you find code examples, include them.",
            config=types.GenerateContentConfig(
                tools=[file_search_tool],
                temperature=0.1,
            ),
        )

        if response.text:
            return response.text
        else:
            return "No relevant information found in the knowledge base."

    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Error searching knowledge base: {str(e)}"


# ============================================================================
# GET POINT BALANCE TOOL
# ============================================================================


@mcp.tool()
def get_point_balance() -> dict:
    """
    Get the user's current point balance from MarketMaya.

    Returns:
        Dictionary containing point_balance, hold_balance, and total balance
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/client/v2/getPointBalance",
                headers=get_auth_headers(),
                json={},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP Error: {e}")
        return {
            "status": "error",
            "message": f"API error: {e.response.status_code} - {e.response.text}",
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch balance: {str(e)}",
        }


# ============================================================================
# GET BACKTEST OPTIONS TOOL
# ============================================================================


@mcp.tool()
def get_backtest_options(strategy_id: str) -> dict:
    """
    Get backtest options for a specific strategy.

    Args:
        strategy_id: The encrypted ID of the strategy (e.g., "mdaB0$Eix..."). NOT the simple numeric ID.

    Returns:
        Dictionary containing available backtest options.
    """
    logger.info(f"Fetching backtest options for strategy_id: {strategy_id}")

    # Ensure ID is a string and strip whitespace
    clean_id = str(strategy_id).strip()
    payload = {"id": clean_id}

    try:
        with httpx.Client(timeout=30.0) as client:
            # Use json parameter which httpx handles correctly (sets Content-Type and Content-Length)
            # But we'll log what we're sending
            logger.info(f"Sending payload: {payload}")

            response = client.post(
                f"{API_BASE_URL}/subscription/getBacktestOptions",
                headers=get_auth_headers(),
                json=payload,
            )

            if response.status_code != 200:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP Error: {e}")
        return {
            "status": "error",
            "message": f"API error: {e.response.status_code} - {e.response.text}",
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch backtest options: {str(e)}",
        }


# ============================================================================
# MODIFY STRATEGY TOOL
# ============================================================================


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
        strategy_id: The encrypted ID of the strategy to modify (e.g., "mdaB0$Eix..."). Get this from get_my_strategies don't ask user for ID.
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
    clean_id = str(strategy_id).strip()
    logger.info(f"🔄 Modifying strategy: {clean_id}")

    try:
        with httpx.Client(timeout=30.0) as client:
            # Step 1: Check if strategy can be edited
            logger.info(f"📤 Checking if strategy can be edited...")
            can_edit_response = client.post(
                f"{API_BASE_URL}/mainStrategy/canEdit",
                headers=get_auth_headers(),
                json={"id": clean_id},
            )

            if can_edit_response.status_code != 200:
                logger.error(f"❌ canEdit API Error: {can_edit_response.text}")
                return {
                    "status": "error",
                    "message": f"Cannot check edit permission: {can_edit_response.text}",
                }

            can_edit_data = can_edit_response.json()
            logger.info(f"📥 canEdit Response: {can_edit_data}")

            # Check if editing is allowed
            if isinstance(can_edit_data, dict):
                if can_edit_data.get("error") or can_edit_data.get("canEdit") == False:
                    error_msg = can_edit_data.get(
                        "message",
                        "Strategy cannot be edited. It may be running or deployed.",
                    )
                    return {
                        "status": "error",
                        "message": error_msg,
                    }

            # Step 2: Get current strategy details to preserve unchanged fields
            logger.info(f"📤 Fetching current strategy details...")
            # We need to get strategy details - use search to find it
            strategies_response = client.post(
                f"{API_BASE_URL}/mainStrategy/getMyStrategies",
                headers=get_auth_headers(),
                json={
                    "skip": 0,
                    "take": 100,
                    "search": "",
                    "symbols": [],
                    "tradingType": "All",
                },
            )

            if strategies_response.status_code != 200:
                logger.error(f"❌ getMyStrategies Error: {strategies_response.text}")
                return {
                    "status": "error",
                    "message": "Failed to fetch current strategy details",
                }

            strategies_data = strategies_response.json()
            current_strategy = None

            # Find the strategy by ID
            if isinstance(strategies_data, dict) and "strategies" in strategies_data:
                for s in strategies_data["strategies"]:
                    if s.get("id") == clean_id:
                        current_strategy = s
                        break

            if not current_strategy:
                return {
                    "status": "error",
                    "message": f"Strategy with ID '{clean_id}' not found",
                }

            logger.info(
                f"📥 Found strategy: {current_strategy.get('strategy_name', 'Unknown')}"
            )

            # Step 3: Build updated payload - merge current with new values
            # Start with current strategy data and update only provided fields
            payload = {
                "id": clean_id,
                "strategy_name": strategy_name
                if strategy_name is not None
                else current_strategy.get("strategy_name", ""),
                "short_description": current_strategy.get("short_description", ""),
                "long_description": current_strategy.get("long_description", ""),
                "strategy_id": current_strategy.get(
                    "strategy_id", "YioJhK5IqBULe8fPLMnXaAaC0$aC0$"
                ),
                "mix_name": current_strategy.get("mix_name", ""),
                "main_exchange": current_strategy.get("main_exchange", "NSE"),
                "main_segment": current_strategy.get("main_segment", "EQ"),
                "main_symbol": current_strategy.get("main_symbol", ""),
                "main_contract": current_strategy.get("main_contract", "NEAR"),
                "main_expiry": current_strategy.get("main_expiry", "MONTHLY"),
                "product_type": product_type
                if product_type is not None
                else current_strategy.get("product_type", "NRML"),
                "exit_order_product_type": current_strategy.get(
                    "exit_order_product_type", ""
                ),
                "qty_type": current_strategy.get("qty_type", "Qty"),
                "qty": quantity
                if quantity is not None
                else current_strategy.get("qty", 1),
                "lot": lot if lot is not None else current_strategy.get("lot", 1),
                "atm": current_strategy.get("atm", 0),
                "strike_price": current_strategy.get("strike_price", 0),
                "option_type": current_strategy.get("option_type", ""),
                "intraday_entry_time": intraday_entry_time
                if intraday_entry_time is not None
                else current_strategy.get("intraday_entry_time", "9:16"),
                "intraday_exit_time": intraday_exit_time
                if intraday_exit_time is not None
                else current_strategy.get("intraday_exit_time", "15:25"),
                "is_intraday": is_intraday
                if is_intraday is not None
                else current_strategy.get("is_intraday", True),
                "jobbing_side": side
                if side is not None
                else current_strategy.get("jobbing_side", "BUY"),
                "jobbing_start_price": jobbing_start_price
                if jobbing_start_price is not None
                else current_strategy.get("jobbing_start_price", 0),
                "jobbing_end_price": jobbing_end_price
                if jobbing_end_price is not None
                else current_strategy.get("jobbing_end_price", 0),
                "average_by": current_strategy.get("average_by", "Point"),
                "average_value": averaging_points
                if averaging_points is not None
                else current_strategy.get("average_value", 100),
                "target_by": current_strategy.get("target_by", "Point"),
                "target": current_strategy.get("target", 0),
                "intraday_target": target_points
                if target_points is not None
                else current_strategy.get("intraday_target", 100),
                "maximum_steps": max_steps
                if max_steps is not None
                else current_strategy.get("maximum_steps", 50),
                "maximum_target_steps": current_strategy.get("maximum_target_steps", 0),
                "sqroff_on_maximum_steps": current_strategy.get(
                    "sqroff_on_maximum_steps", False
                ),
                "calculate_qty_on_market_jump": current_strategy.get(
                    "calculate_qty_on_market_jump", False
                ),
                "allow_update_parameters": current_strategy.get(
                    "allow_update_parameters", True
                ),
                "order_type": order_type
                if order_type is not None
                else current_strategy.get("order_type", "Market Order"),
                "no_of_limit_order_retry": current_strategy.get(
                    "no_of_limit_order_retry", 0
                ),
                "retry_at_every_seconds": current_strategy.get(
                    "retry_at_every_seconds", 0
                ),
                "market_order_after_retry": current_strategy.get(
                    "market_order_after_retry", False
                ),
                "reset_cycle_by_master_tpsl": current_strategy.get(
                    "reset_cycle_by_master_tpsl", False
                ),
                "rollover_before_days": current_strategy.get("rollover_before_days", 0),
                "is_auto_rollover": current_strategy.get("is_auto_rollover", False),
                "is_add_hedge_leg": current_strategy.get("is_add_hedge_leg", False),
                "rollover_time": current_strategy.get("rollover_time", "0:0"),
                "master_tp_money": master_tp_money
                if master_tp_money is not None
                else current_strategy.get("master_tp_money", 0),
                "master_sl_money": master_sl_money
                if master_sl_money is not None
                else current_strategy.get("master_sl_money", 0),
                "reset_cycle_on_positive_mtm": current_strategy.get(
                    "reset_cycle_on_positive_mtm", 0
                ),
                "required_margin": required_margin
                if required_margin is not None
                else current_strategy.get("required_margin", 100000),
                "is_trail_sl": is_trail_sl
                if is_trail_sl is not None
                else current_strategy.get("is_trail_sl", False),
                "profit_move": profit_move
                if profit_move is not None
                else current_strategy.get("profit_move", 0),
                "sl_move": sl_move
                if sl_move is not None
                else current_strategy.get("sl_move", 0),
                "no_of_trail_sl": no_of_trail_sl
                if no_of_trail_sl is not None
                else current_strategy.get("no_of_trail_sl", 0),
                "scalping_opening_qty": current_strategy.get("scalping_opening_qty", 0),
                "increase_qty_on_avg": current_strategy.get(
                    "increase_qty_on_avg", False
                ),
                "increase_qty": current_strategy.get("increase_qty", 0),
                "increase_qty_type": current_strategy.get("increase_qty_type", "Qty"),
                "rebacktest": False,
                "sub": current_strategy.get("sub", []),
                "effect_all_sub_strategies": False,
            }

            # Step 4: Update the strategy
            logger.info(f"📤 Updating strategy with new parameters...")
            update_response = client.post(
                f"{API_BASE_URL}/mainStrategy/createScalpingStrategy",
                headers=get_auth_headers(),
                json=payload,
            )

            logger.info(f"📥 Update Response Status: {update_response.status_code}")

            if update_response.status_code != 200:
                try:
                    error_data = update_response.json()
                    error_msg = error_data.get(
                        "message", error_data.get("error", update_response.text)
                    )
                except Exception:
                    error_msg = update_response.text
                logger.error(f"❌ Update Error: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Failed to update strategy: {error_msg}",
                }

            update_data = update_response.json()
            logger.info(f"📥 Update Response: {update_data}")

            # Build summary of changes
            changes = []
            if strategy_name is not None:
                changes.append(f"Name: {strategy_name}")
            if averaging_points is not None:
                changes.append(f"Averaging Points: {averaging_points}")
            if target_points is not None:
                changes.append(f"Target Points: {target_points}")
            if max_steps is not None:
                changes.append(f"Max Steps: {max_steps}")
            if quantity is not None:
                changes.append(f"Quantity: {quantity}")
            if side is not None:
                changes.append(f"Side: {side}")
            if is_intraday is not None:
                changes.append(f"Intraday: {is_intraday}")
            if master_tp_money is not None:
                changes.append(f"Master TP: {master_tp_money}")
            if master_sl_money is not None:
                changes.append(f"Master SL: {master_sl_money}")

            return {
                "status": "success",
                "message": f"Strategy updated successfully!",
                "changes": changes if changes else ["No specific changes provided"],
                "strategy_name": payload["strategy_name"],
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP Error: {e}")
        return {
            "status": "error",
            "message": f"API error: {e.response.status_code} - {e.response.text}",
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Failed to modify strategy: {str(e)}",
        }


if __name__ == "__main__":
    mcp.run()
