from fastmcp import FastMCP
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
import httpx
import os
import logging
import sys
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tool_loader import fetch_and_register_tools

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
FETCH_BEARER_TOKEN = os.getenv("FETCH_BEARER_TOKEN", "")

# Optional source field used by some APIs
SOURCE = os.getenv("SOURCE", "MCP")
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


# @mcp.tool()
# def create_scalping_strategy(
#     strategy_name: str,
#     symbol: str,
#     exchange: Literal["NSE", "MCX", "BSE"] = "NSE",
#     segment: Literal["EQ", "FUT", "OPT"] = "EQ",
#     contract: Literal["NEAR", "NEXT", "FAR"] = "NEAR",
#     expiry: Literal["MONTHLY", "WEEKLY"] = "MONTHLY",
#     averaging_points: int = 100,
#     avg_points: Optional[int] = None,  # Alias for averaging_points
#     target_points: int = 100,
#     max_steps: int = 50,
#     quantity: int = 1,
#     lot: int = 1,
#     side: Literal["BUY", "SELL"] = "BUY",
#     is_intraday: bool = True,
#     intraday_entry_time: str = "9:16",
#     intraday_exit_time: str = "15:25",
#     required_margin: int = 100000,
#     product_type: Literal["NRML", "MIS", "CNC"] = "NRML",
#     order_type: Literal["Market Order", "Limit Order"] = "Market Order",
#     # Price range settings
#     jobbing_start_price: float = 0,
#     jobbing_end_price: float = 0,
#     # Averaging settings
#     average_by: Literal["Point", "Percent"] = "Point",
#     target_by: Literal["Point", "Percent"] = "Point",
#     maximum_target_steps: int = 0,
#     sqroff_on_maximum_steps: bool = False,
#     calculate_qty_on_market_jump: bool = False,
#     # Quantity increase settings
#     increase_qty_on_avg: bool = False,
#     increase_qty: int = 0,
#     increase_qty_type: Literal["Qty", "Lot"] = "Qty",
#     scalping_opening_qty: int = 0,
#     # Limit order settings
#     no_of_limit_order_retry: int = 0,
#     retry_at_every_seconds: int = 0,
#     market_order_after_retry: bool = False,
#     # Rollover settings
#     is_auto_rollover: bool = False,
#     rollover_before_days: int = 0,
#     rollover_time: str = "0:0",
#     # Master TP/SL settings
#     reset_cycle_by_master_tpsl: bool = False,
#     master_tp_money: int = 0,
#     master_sl_money: int = 0,
#     reset_cycle_on_positive_mtm: int = 0,
#     # Trail SL settings
#     is_trail_sl: bool = False,
#     profit_move: int = 0,
#     sl_move: int = 0,
#     no_of_trail_sl: int = 0,
#     # Options settings
#     atm: int = 0,
#     strike_price: int = 0,
#     option_type: Literal["CE", "PE"] = "CE",
#     # Other settings
#     allow_update_parameters: bool = True,
#     is_add_hedge_leg: bool = False,
# ) -> dict:
#     """
#     Create and deploy a scalping strategy to MarketMaya.

#     Args:
#         strategy_name: Name of the strategy (e.g., "RELIANCE Scalping") if user did not provide then create appropriate name
#         symbol: Trading symbol (e.g., RELIANCE, SILVER, NIFTY)
#         exchange: Exchange - NSE, MCX, or BSE (default: NSE)
#         segment: Market segment - EQ (Equity), FUT (Futures), OPT (Options) (default: EQ)
#         contract: Contract type for FUT/OPT - NEAR, NEXT, FAR (default: NEAR)
#         expiry: Expiry type for FUT/OPT - MONTHLY or WEEKLY (default: MONTHLY)
#         averaging_points: Points interval for averaging down (default: 100)
#         target_points: Target profit in points (default: 100)
#         max_steps: Maximum number of averaging steps (default: 50)
#         quantity: Quantity per trade (default: 1)
#         lot: Lot size multiplier (default: 1)
#         side: Trade direction - BUY or SELL (default: BUY)
#         is_intraday: Whether this is an intraday strategy (default: True)
#         intraday_entry_time: Entry time for intraday in HH:MM format (default: "9:16")
#         intraday_exit_time: Exit time for intraday in HH:MM format (default: "15:25")
#         required_margin: Required margin for the strategy (default: 100000)
#         product_type: Product type - NRML, MIS, CNC (default: NRML)
#         order_type: Order type - Market Order or Limit Order (default: Market Order)
#         jobbing_start_price: Start price for price range (default: 0 = no limit)
#         jobbing_end_price: End price for price range (default: 0 = no limit)
#         average_by: Average calculation method - Point or Percent (default: Point)
#         target_by: Target calculation method - Point or Percent (default: Point)
#         maximum_target_steps: Max target steps before booking (default: 0)
#         sqroff_on_maximum_steps: Square off when max steps reached (default: False)
#         calculate_qty_on_market_jump: Adjust qty on market gap (default: False)
#         increase_qty_on_avg: Increase quantity on averaging (default: False)
#         increase_qty: Amount to increase quantity by (default: 0)
#         increase_qty_type: Type for qty increase - Qty or Lot (default: None)
#         scalping_opening_qty: Opening quantity for scalping (default: 0)
#         no_of_limit_order_retry: Number of limit order retries (default: 0)
#         retry_at_every_seconds: Seconds between retries (default: 0)
#         market_order_after_retry: Place market order after retry fails (default: False)
#         is_auto_rollover: Enable auto rollover for FUT/OPT (default: False)
#         rollover_before_days: Days before expiry to rollover (default: 0)
#         rollover_time: Time to perform rollover in HH:MM (default: "0:0")
#         reset_cycle_by_master_tpsl: Reset cycle on master TP/SL hit (default: False)
#         master_tp_money: Master take profit in money (default: 0)
#         master_sl_money: Master stop loss in money (default: 0)
#         reset_cycle_on_positive_mtm: Reset when MTM reaches this positive value (default: 0)
#         is_trail_sl: Enable trailing stop loss (default: False)
#         profit_move: Points profit to trigger trail (default: 0)
#         sl_move: Points to move SL by (default: 0)
#         no_of_trail_sl: Number of trail SL moves (default: 0)
#         atm: ATM strike offset for options (default: 0)
#         strike_price: Specific strike price for options (default: 0)
#         option_type: Option type - CE or PE (default: "")
#         allow_update_parameters: Allow parameter updates (default: True)
#         is_add_hedge_leg: Add hedge leg to strategy (default: False)

#     Returns:
#         API response with strategy ID and deployment status
#     """

#     # Handle alias for averaging_points
#     if avg_points is not None:
#         averaging_points = avg_points

#     # Build mix_name based on segment
#     if segment == "EQ":
#         mix_name = f"{symbol} {segment} {exchange}"
#     else:
#         mix_name = f"{symbol} {segment} {contract} {expiry}"

#     # Build short and long descriptions
#     short_desc = f"{side} {symbol} at every {averaging_points} points"
#     long_desc = f"{side} {symbol} at every {averaging_points} points down side and book profit at {target_points} points."

#     # Create the strategy payload with ALL parameters
#     payload = {
#         "id": "",
#         "strategy_name": strategy_name,
#         "short_description": short_desc,
#         "long_description": long_desc,
#         "strategy_id": "YioJhK5IqBULe8fPLMnXaAaC0$aC0$",  # Scalping plugin ID
#         "mix_name": mix_name,
#         "main_exchange": exchange,
#         "main_segment": segment,
#         "main_symbol": symbol,
#         "main_contract": contract,
#         "main_expiry": expiry,
#         "product_type": product_type,
#         "exit_order_product_type": "",
#         "qty_type": "Qty",
#         "qty": quantity,
#         "lot": lot,
#         "atm": atm,
#         "strike_price": strike_price,
#         "option_type": option_type,
#         "intraday_entry_time": intraday_entry_time,
#         "intraday_exit_time": intraday_exit_time,
#         "is_intraday": is_intraday,
#         "jobbing_side": side,
#         "jobbing_start_price": jobbing_start_price,
#         "jobbing_end_price": jobbing_end_price,
#         "average_by": average_by,
#         "average_value": averaging_points,
#         "target_by": target_by,
#         "target": 0,
#         "intraday_target": target_points,
#         "maximum_steps": max_steps,
#         "maximum_target_steps": maximum_target_steps,
#         "sqroff_on_maximum_steps": sqroff_on_maximum_steps,
#         "calculate_qty_on_market_jump": calculate_qty_on_market_jump,
#         "allow_update_parameters": allow_update_parameters,
#         "order_type": order_type,
#         "no_of_limit_order_retry": no_of_limit_order_retry,
#         "retry_at_every_seconds": retry_at_every_seconds,
#         "market_order_after_retry": market_order_after_retry,
#         "reset_cycle_by_master_tpsl": reset_cycle_by_master_tpsl,
#         "rollover_before_days": rollover_before_days,
#         "is_auto_rollover": is_auto_rollover,
#         "is_add_hedge_leg": is_add_hedge_leg,
#         "rollover_time": rollover_time,
#         "master_tp_money": master_tp_money,
#         "master_sl_money": master_sl_money,
#         "reset_cycle_on_positive_mtm": reset_cycle_on_positive_mtm,
#         "required_margin": required_margin,
#         "is_trail_sl": is_trail_sl,
#         "profit_move": profit_move,
#         "sl_move": sl_move,
#         "no_of_trail_sl": no_of_trail_sl,
#         "scalping_opening_qty": scalping_opening_qty,
#         "increase_qty_on_avg": increase_qty_on_avg,
#         "increase_qty": increase_qty,
#         "increase_qty_type": increase_qty_type,
#         "rebacktest": False,
#         "sub": [],
#         "effect_all_sub_strategies": False,
#     }

#     logger.info(f"🚀 Creating strategy: {strategy_name} for {symbol}")
#     logger.info(f"   Exchange: {exchange}, Segment: {segment}, Side: {side}")
#     logger.info(
#         f"   Avg: {averaging_points} pts, Target: {target_points} pts, Max Steps: {max_steps}"
#     )

#     # Make API call to create the strategy
#     try:
#         logger.info(
#             f"📤 Calling API: {API_BASE_URL}/mainStrategy/createScalpingStrategy"
#         )
#         with httpx.Client(timeout=30.0) as client:
#             response = client.post(
#                 f"{API_BASE_URL}/mainStrategy/createScalpingStrategy",
#                 headers=get_auth_headers(),
#                 json=payload,
#             )

#             logger.info(f"📥 API Response Status: {response.status_code}")

#             # Check for API errors before raising
#             if response.status_code != 200:
#                 try:
#                     error_data = response.json()
#                     error_msg = error_data.get(
#                         "message", error_data.get("error", response.text)
#                     )
#                 except Exception:
#                     error_msg = response.text
#                 logger.error(f"❌ API Error: {error_msg}")
#                 return {
#                     "status": "error",
#                     "message": f"API returned error: {error_msg}",
#                 }

#             api_response = response.json()
#             logger.info(f"📥 API Response: {api_response}")

#             # Handle list response (assume success if list is returned)
#             if isinstance(api_response, list):
#                 logger.info("✅ API returned a list, assuming success.")
#                 # Try to find an ID in the first element if available
#                 strategy_id = "N/A"
#                 if api_response and isinstance(api_response[0], dict):
#                     strategy_id = api_response[0].get("id", "N/A")

#                 return {
#                     "status": "success",
#                     "message": f"Strategy '{strategy_name}' created successfully!",
#                     "strategy_id": strategy_id,
#                     "details": api_response,
#                 }

#             # Check if response indicates an error
#             if api_response.get("error") or api_response.get("status") == "error":
#                 error_msg = api_response.get(
#                     "message", api_response.get("error", "Unknown API error")
#                 )
#                 logger.error(f"❌ API returned error status: {error_msg}")
#                 return {
#                     "status": "error",
#                     "message": error_msg,
#                 }

#             logger.info(
#                 f"✅ Strategy created successfully! ID: {api_response.get('id', 'N/A')}"
#             )
#             return {
#                 "status": "success",
#                 "message": f"Strategy '{strategy_name}' created successfully!",
#                 "strategy_id": api_response.get("id", ""),
#             }
#     except httpx.HTTPStatusError as e:
#         logger.error(f"❌ HTTP Error: {e}")
#         try:
#             error_data = e.response.json()
#             error_msg = error_data.get("message", error_data.get("error", str(e)))
#         except Exception:
#             error_msg = e.response.text
#         logger.error(f"❌ Error message: {error_msg}")
#         return {
#             "status": "error",
#             "message": f"API error: {error_msg}",
#         }
#     except Exception as e:
#         logger.error(f"❌ Unexpected error: {e}")
#         import traceback

#         logger.error(f"❌ Traceback: {traceback.format_exc()}")
#         return {
#             "status": "error",
#             "message": f"Failed to create strategy: {str(e)}",
#         }


# ============================================================================
# GET MY STRATEGIES TOOL
# ============================================================================


# @mcp.tool()
# def get_my_strategies(
#     skip: int = 0,
#     take: int = 10,
#     search: str = "",
#     symbols: Optional[List[str]] = None,
#     trading_type: Literal["All", "INTRADAY", "POSITIONAL"] = "All",
#     sort_by: Literal["newest", "oldest", "name"] = "newest",
# ) -> dict:
#     """
#     Get list of user's trading strategies from MarketMaya.

#     Args:
#         skip: Number of strategies to skip for pagination (default: 0)
#         take: Number of strategies to fetch (default: 10)
#         search: Search term to filter strategies by name (default: "")
#         symbols: List of symbols to filter by (default: None for all)
#         trading_type: Filter by trading type - All, INTRADAY, POSITIONAL (default: All)
#         sort_by: Sort order - newest, oldest, name (default: newest)

#     Returns:
#         List of strategies with their details
#     """

#     # Build request payload
#     payload = {
#         "skip": skip,
#         "take": take,
#         "search": search,
#         "symbols": symbols or [],
#         "tradingType": trading_type,
#         "strategyMasterIds": [],
#         "strategyMaster": {"id": "", "strategy_name": "All Plugins", "selected": True},
#         "AuthorIds": [],
#         "sortBy": sort_by,
#     }

#     # Make API call
#     try:
#         with httpx.Client(timeout=30.0) as client:
#             response = client.post(
#                 f"{API_BASE_URL}/V3/mainStrategy/getClientMyStrategy",
#                 headers=get_auth_headers(),
#                 json=payload,
#             )
#             response.raise_for_status()
#             api_response = response.json()

#             # Extract relevant data
#             strategies = []
#             for strategy in api_response.get("data", []):
#                 strategies.append(
#                     {
#                         "id": strategy.get("id"),
#                         "sid": strategy.get("sid"),
#                         "name": strategy.get("strategy_name"),
#                         "plugin": strategy.get("plugin_name"),
#                         "symbol": strategy.get("main_symbol"),
#                         "trading_type": strategy.get("trading_type"),
#                         "required_margin": strategy.get("required_margin_format"),
#                         "is_deployed": strategy.get("is_deployed"),
#                         "created_on": strategy.get("created_on"),
#                         "type": strategy.get("type"),
#                     }
#                 )

#             return {
#                 "status": "success",
#                 "total": api_response.get("total", 0),
#                 "strategies": strategies,
#                 "available_symbols": api_response.get("symbols", []),
#             }
#     except httpx.HTTPStatusError as e:
#         return {
#             "status": "error",
#             "message": f"API error: {e.response.status_code} - {e.response.text}",
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Failed to fetch strategies: {str(e)}",
#         }


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
    
    # Try to load store name from config file first, then env var
    store_name = os.getenv("MMCOPILOT_STORE_NAME")
    config_path = os.path.join(os.path.dirname(__file__), "store_config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                if config.get("store_name"):
                    store_name = config.get("store_name")
                    logger.info(f"Loaded store name from config: {store_name}")
        except Exception as e:
            logger.error(f"Failed to load store config: {e}")

    if not api_key:
        return "Error: GEMINI_API_KEY not configured in MCP server."

    if not store_name:
        return "Error: Knowledge base not configured (MMCOPILOT_STORE_NAME missing and no store_config.json found)."

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
                system_instruction="You retrive information from the knowledge base to help the user. Provide detailed and helpful answers based on the documents you find. and if not found say no relevant information found.",
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


# @mcp.tool()
# def get_point_balance() -> dict:
#     """
#     Get the user's current point balance from MarketMaya.

#     Returns:
#         Dictionary containing point_balance, hold_balance, and total balance
#     """
#     try:
#         with httpx.Client(timeout=30.0) as client:
#             response = client.post(
#                 f"{API_BASE_URL}/client/v2/getPointBalance",
#                 headers=get_auth_headers(),
#                 json={},
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as e:
#         logger.error(f"❌ HTTP Error: {e}")
#         return {
#             "status": "error",
#             "message": f"API error: {e.response.status_code} - {e.response.text}",
#         }
#     except Exception as e:
#         logger.error(f"❌ Unexpected error: {e}")
#         return {
#             "status": "error",
#             "message": f"Failed to fetch balance: {str(e)}",
#         }


# ============================================================================
# GET BACKTEST OPTIONS TOOL
# ============================================================================


# @mcp.tool()
# def get_backtest_options(strategy_id: str) -> dict:
#     """
#     Get backtest options for a specific strategy.

#     Args:
#         strategy_id: The encrypted ID of the strategy (e.g., "mdaB0$Eix..."). NOT the simple numeric ID.

#     Returns:
#         Dictionary containing available backtest options.
#     """
#     logger.info(f"Fetching backtest options for strategy_id: {strategy_id}")

#     # Ensure ID is a string and strip whitespace
#     clean_id = str(strategy_id).strip()
#     payload = {"id": clean_id}

#     try:
#         with httpx.Client(timeout=30.0) as client:
#             # Use json parameter which httpx handles correctly (sets Content-Type and Content-Length)
#             # But we'll log what we're sending
#             logger.info(f"Sending payload: {payload}")

#             response = client.post(
#                 f"{API_BASE_URL}/subscription/getBacktestOptions",
#                 headers=get_auth_headers(),
#                 json=payload,
#             )

#             if response.status_code != 200:
#                 logger.error(f"❌ API Error {response.status_code}: {response.text}")

#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as e:
#         logger.error(f"❌ HTTP Error: {e}")
#         return {
#             "status": "error",
#             "message": f"API error: {e.response.status_code} - {e.response.text}",
#         }
#     except Exception as e:
#         logger.error(f"❌ Unexpected error: {e}")
#         return {
#             "status": "error",
#             "message": f"Failed to fetch backtest options: {str(e)}",
#         }


# ============================================================================
# MODIFY STRATEGY TOOL
# ============================================================================


# @mcp.tool()
# def modify_strategy(
#     strategy_id: str,
#     strategy_name: Optional[str] = None,
#     averaging_points: Optional[int] = None,
#     target_points: Optional[int] = None,
#     max_steps: Optional[int] = None,
#     quantity: Optional[int] = None,
#     lot: Optional[int] = None,
#     side: Optional[Literal["BUY", "SELL"]] = None,
#     is_intraday: Optional[bool] = None,
#     intraday_entry_time: Optional[str] = None,
#     intraday_exit_time: Optional[str] = None,
#     required_margin: Optional[int] = None,
#     product_type: Optional[Literal["NRML", "MIS", "CNC"]] = None,
#     order_type: Optional[Literal["Market Order", "Limit Order"]] = None,
#     jobbing_start_price: Optional[float] = None,
#     jobbing_end_price: Optional[float] = None,
#     master_tp_money: Optional[int] = None,
#     master_sl_money: Optional[int] = None,
#     is_trail_sl: Optional[bool] = None,
#     profit_move: Optional[int] = None,
#     sl_move: Optional[int] = None,
#     no_of_trail_sl: Optional[int] = None,
# ) -> dict:
#     """
#      Modify an existing scalping strategy on MarketMaya.

#     This tool first checks if the strategy can be edited, then updates it with the new parameters.

#     Args:
#         strategy_id: The encrypted ID of the strategy to modify (e.g., "mdaB0$Eix..."). Get this from get_my_strategies.
#         strategy_name: New name for the strategy (optional)
#         averaging_points: New points interval for averaging (optional)
#         target_points: New target profit in points (optional)
#         max_steps: New maximum averaging steps (optional)
#         quantity: New quantity per trade (optional)
#         lot: New lot size multiplier (optional)
#         side: New trade direction - BUY or SELL (optional)
#         is_intraday: Whether strategy is intraday (optional)
#         intraday_entry_time: New entry time HH:MM (optional)
#         intraday_exit_time: New exit time HH:MM (optional)
#         required_margin: New required margin (optional)
#         product_type: New product type - NRML, MIS, CNC (optional)
#         order_type: New order type (optional)
#         jobbing_start_price: New start price range (optional)
#         jobbing_end_price: New end price range (optional)
#         master_tp_money: New master take profit (optional)
#         master_sl_money: New master stop loss (optional)
#         is_trail_sl: Enable/disable trailing SL (optional)
#         profit_move: New profit trigger points (optional)
#         sl_move: New SL move points (optional)
#         no_of_trail_sl: New number of trail SL moves (optional)

#     Returns:
#         API response with update status
#     """
#     clean_id = str(strategy_id).strip()
#     logger.info("Modifying strategy (simple): %s", clean_id)

#     try:
#         with httpx.Client(timeout=30.0) as client:
#             # canEdit check
#             logger.info(
#                 "Calling API: mainStrategy/canEdit with payload: %s", {"id": clean_id}
#             )
#             print("REQUEST -> mainStrategy/canEdit:\n", {"id": clean_id})
#             can_edit_resp = client.post(
#                 f"{API_BASE_URL}/mainStrategy/canEdit",
#                 headers=get_auth_headers(),
#                 json={"id": clean_id},
#             )
#             try:
#                 can_edit_json = can_edit_resp.json()
#             except Exception:
#                 can_edit_json = {"text": can_edit_resp.text}

#             logger.info("canEdit response status: %s", can_edit_resp.status_code)
#             logger.info("canEdit response body: %s", can_edit_json)
#             print("RESPONSE <- mainStrategy/canEdit:\n", can_edit_json)

#             if can_edit_resp.status_code != 200:
#                 return {"status": "error", "message": "Cannot check edit permission"}
#             if isinstance(can_edit_json, dict) and (
#                 can_edit_json.get("error") or can_edit_json.get("canEdit") is False
#             ):
#                 return {
#                     "status": "error",
#                     "message": can_edit_json.get(
#                         "message", "Strategy cannot be edited"
#                     ),
#                 }

#             params = {
#                 "strategy_id": strategy_id,
#                 "strategy_name": strategy_name,
#                 "averaging_points": averaging_points,
#                 "target_points": target_points,
#                 "max_steps": max_steps,
#                 "quantity": quantity,
#                 "lot": lot,
#                 "side": side,
#                 "is_intraday": is_intraday,
#                 "intraday_entry_time": intraday_entry_time,
#                 "intraday_exit_time": intraday_exit_time,
#                 "required_margin": required_margin,
#                 "product_type": product_type,
#                 "order_type": order_type,
#                 "jobbing_start_price": jobbing_start_price,
#                 "jobbing_end_price": jobbing_end_price,
#                 "master_tp_money": master_tp_money,
#                 "master_sl_money": master_sl_money,
#                 "is_trail_sl": is_trail_sl,
#                 "profit_move": profit_move,
#                 "sl_move": sl_move,
#                 "no_of_trail_sl": no_of_trail_sl,
#             }
#             try:
#                 logger.info(
#                     "modify_strategy called with params: %s",
#                     json.dumps(params, default=str),
#                 )
#             except Exception:
#                 logger.info("modify_strategy called with params: %s", params)
#             # also print to stdout for immediate visibility
#             print("modify_strategy incoming params:\n", params)

#             # Fetch the full current scalping record and merge user-provided fields
#             try:
#                 get_payload = {"id": clean_id}
#                 if SOURCE:
#                     get_payload["source"] = SOURCE

#                 headers = get_auth_headers()
#                 headers_preview = dict(headers)
#                 auth = headers_preview.get("Authorization")
#                 if isinstance(auth, str) and auth.startswith("Bearer "):
#                     token_part = auth.split(" ", 1)[1]
#                     headers_preview["Authorization"] = "Bearer " + (token_part[:8] + "..." + token_part[-8:] if len(token_part) > 16 else token_part)

#                 logger.info("Fetching current strategy via getScalpingRecord: %s", get_payload)
#                 logger.info("Request headers (redacted): %s", headers_preview)
#                 get_resp = client.post(f"{API_BASE_URL}/mainStrategy/getScalpingRecord", headers=headers, json=get_payload)
#                 try:
#                     current = get_resp.json()
#                 except Exception:
#                     current = {"text": get_resp.text}

#                 logger.info("getScalpingRecord status: %s", get_resp.status_code)
#                 logger.info("getScalpingRecord body: %s", current)

#                 if get_resp.status_code != 200 or not isinstance(current, dict):
#                     logger.warning("Could not fetch full strategy record; falling back to minimal update payload")
#                     current = {"id": clean_id}

#             except Exception as e:
#                 logger.exception("Error fetching current strategy record: %s", e)
#                 current = {"id": clean_id}

#             # Helper to set field only when user provided a non-None value
#             def set_if(provided, key):
#                 if provided is not None:
#                     current[key] = provided

#             set_if(strategy_name, "strategy_name")
#             set_if(averaging_points, "average_value")
#             set_if(target_points, "intraday_target")
#             set_if(max_steps, "maximum_steps")
#             set_if(quantity, "qty")
#             set_if(lot, "lot")
#             set_if(side, "jobbing_side")
#             set_if(is_intraday, "is_intraday")
#             set_if(intraday_entry_time, "intraday_entry_time")
#             set_if(intraday_exit_time, "intraday_exit_time")
#             set_if(required_margin, "required_margin")
#             set_if(product_type, "product_type")
#             set_if(order_type, "order_type")
#             set_if(jobbing_start_price, "jobbing_start_price")
#             set_if(jobbing_end_price, "jobbing_end_price")
#             set_if(master_tp_money, "master_tp_money")
#             set_if(master_sl_money, "master_sl_money")
#             set_if(is_trail_sl, "is_trail_sl")
#             set_if(profit_move, "profit_move")
#             set_if(sl_move, "sl_move")
#             set_if(no_of_trail_sl, "no_of_trail_sl")

#             current["id"] = clean_id

#             # Send merged payload to update endpoint
#             logger.info("Calling API: mainStrategy/createScalpingStrategy with merged payload keys: %s", list(current.keys()))
#             print("REQUEST -> mainStrategy/createScalpingStrategy:\n", current)
#             upd_resp = client.post(f"{API_BASE_URL}/mainStrategy/createScalpingStrategy", headers=get_auth_headers(), json=current, timeout=30.0)
#             try:
#                 upd_json = upd_resp.json()
#             except Exception:
#                 upd_json = {"text": upd_resp.text}

#             logger.info("createScalpingStrategy response status: %s", upd_resp.status_code)
#             logger.info("createScalpingStrategy response body: %s", upd_json)
#             print("RESPONSE <- mainStrategy/createScalpingStrategy:\n", upd_json)

#             if upd_resp.status_code != 200:
#                 try:
#                     err = upd_json if isinstance(upd_json, dict) else {"text": upd_json}
#                     return {"status": "error", "message": err.get("message", upd_resp.text) if isinstance(err, dict) else str(err), "response": upd_json}
#                 except Exception:
#                     return {"status": "error", "message": upd_resp.text, "response": upd_json}

#             return {"status": "success", "message": "Strategy update called", "response": upd_json}

#     except httpx.HTTPStatusError as e:
#         logger.error("HTTP Error while modifying strategy: %s", e)
#         return {
#             "status": "error",
#             "message": f"API error: {e.response.status_code} - {e.response.text}",
#         }
#     except Exception as e:
#         logger.error("Unexpected error while modifying strategy: %s", e)
#         import traceback

#         logger.error("Traceback: %s", traceback.format_exc())
#         return {"status": "error", "message": f"Failed to modify strategy: {str(e)}"}


if __name__ == "__main__":
    # Register dynamic tools from API
    fetch_and_register_tools(mcp, API_BASE_URL, FETCH_BEARER_TOKEN)
    mcp.run()
