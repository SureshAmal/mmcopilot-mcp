# server.py
from fastmcp import FastMCP
from typing import Optional, Literal
from pydantic import BaseModel, Field

mcp = FastMCP("Trading Strategy MCP")


class StrategyPayload(BaseModel):
    """Trading strategy configuration payload"""

    id: str = ""
    strategy_name: str
    short_description: str
    long_description: str
    strategy_id: str
    mix_name: str
    main_exchange: str
    main_segment: str
    main_symbol: str
    main_contract: str
    main_expiry: str
    product_type: str
    exit_order_product_type: str = ""
    qty_type: str
    qty: int
    lot: int
    atm: int
    strike_price: int
    option_type: str = ""
    intraday_entry_time: str
    intraday_exit_time: str
    is_intraday: bool
    jobbing_side: str
    jobbing_start_price: int
    jobbing_end_price: int
    average_by: str
    average_value: int
    target_by: str
    target: int
    intraday_target: int
    maximum_steps: int
    maximum_target_steps: int
    sqroff_on_maximum_steps: bool
    calculate_qty_on_market_jump: bool
    allow_update_parameters: bool
    order_type: str
    no_of_limit_order_retry: int
    retry_at_every_seconds: int
    market_order_after_retry: bool
    reset_cycle_by_master_tpsl: bool
    rollover_before_days: int
    is_auto_rollover: bool
    rollover_time: str
    master_tp_money: int
    master_sl_money: int
    reset_cycle_on_positive_mtm: int
    required_margin: int
    is_trail_sl: bool
    profit_move: int
    sl_move: int
    no_of_trail_sl: int
    scalping_opening_qty: int
    increase_qty_on_avg: bool
    increase_qty: int
    increase_qty_type: Optional[str] = None
    rebacktest: bool
    effect_all_sub_strategies: bool


class StrategyResponse(BaseModel):
    """Response from strategy deployment"""

    client_id: int
    is_deployed: bool
    id: int
    execution_level: str


@mcp.tool()
def create_strategy(
    strategy_name: str,
    symbol: str,
    exchange: str = "NSE",
    segment: str = "EQ",
    qty: int = 1,
    average_value: int = 100,
    intraday_target: int = 100,
    maximum_steps: int = 50,
    jobbing_side: Literal["BUY", "SELL"] = "BUY",
    is_intraday: bool = False,
) -> dict:
    """
    Create a new trading strategy with basic parameters.

    Args:
        strategy_name: Name of the strategy
        symbol: Trading symbol (e.g., RELIANCE)
        exchange: Exchange name (default: NSE)
        segment: Market segment (default: EQ)
        qty: Quantity to trade (default: 1)
        average_value: Averaging interval in points (default: 100)
        intraday_target: Target profit in points (default: 100)
        maximum_steps: Maximum averaging steps (default: 50)
        jobbing_side: Trade direction - BUY or SELL (default: BUY)
        is_intraday: Whether this is an intraday strategy (default: False)

    Returns:
        Strategy deployment response
    """

    # Create the strategy payload
    payload = {
        "id": "",
        "strategy_name": strategy_name,
        "short_description": f"{jobbing_side} {symbol} at every {average_value} points",
        "long_description": f"{jobbing_side} {symbol} at every {average_value} points down side and book profit at {intraday_target} points.",
        "strategy_id": "YioJhK5IqBULe8fPLMnXaAaC0$aC0$",  # This should be generated
        "mix_name": f"{symbol} {segment} {exchange}",
        "main_exchange": exchange,
        "main_segment": segment,
        "main_symbol": symbol,
        "main_contract": "NEAR",
        "main_expiry": "MONTHLY",
        "product_type": "NRML",
        "exit_order_product_type": "",
        "qty_type": "Qty",
        "qty": qty,
        "lot": 1,
        "atm": 0,
        "strike_price": 0,
        "option_type": "",
        "intraday_entry_time": "9:16",
        "intraday_exit_time": "15:25",
        "is_intraday": is_intraday,
        "jobbing_side": jobbing_side,
        "jobbing_start_price": 0,
        "jobbing_end_price": 0,
        "average_by": "Point",
        "average_value": average_value,
        "target_by": "Point",
        "target": 0,
        "intraday_target": intraday_target,
        "maximum_steps": maximum_steps,
        "maximum_target_steps": 0,
        "sqroff_on_maximum_steps": False,
        "calculate_qty_on_market_jump": False,
        "allow_update_parameters": True,
        "order_type": "Market Order",
        "no_of_limit_order_retry": 0,
        "retry_at_every_seconds": 0,
        "market_order_after_retry": False,
        "reset_cycle_by_master_tpsl": False,
        "rollover_before_days": 0,
        "is_auto_rollover": False,
        "rollover_time": "0:0",
        "master_tp_money": 0,
        "master_sl_money": 0,
        "reset_cycle_on_positive_mtm": 0,
        "required_margin": 100000,
        "is_trail_sl": False,
        "profit_move": 0,
        "sl_move": 0,
        "no_of_trail_sl": 0,
        "scalping_opening_qty": 0,
        "increase_qty_on_avg": False,
        "increase_qty": 0,
        "increase_qty_type": None,
        "rebacktest": False,
        "effect_all_sub_strategies": False,
    }

    # Simulate successful response
    response = [
        {
            "client_id": 40495,
            "is_deployed": False,
            "id": 416156,
            "execution_level": "Level 1",
        }
    ]

    return {"payload": payload, "response": response, "status": "success"}


def _build_strategy_payload(
    strategy_name: str,
    symbol: str,
    exchange: str,
    segment: str,
    qty: int,
    average_value: int,
    intraday_target: int,
    maximum_steps: int,
    jobbing_side: str,
    is_intraday: bool,
) -> dict:
    """Internal helper to build strategy payload"""

    payload = {
        "id": "",
        "strategy_name": strategy_name,
        "short_description": f"{jobbing_side} {symbol} at every {average_value} points",
        "long_description": f"{jobbing_side} {symbol} at every {average_value} points down side and book profit at {intraday_target} points.",
        "strategy_id": "YioJhK5IqBULe8fPLMnXaAaC0$aC0$",
        "mix_name": f"{symbol} {segment} {exchange}",
        "main_exchange": exchange,
        "main_segment": segment,
        "main_symbol": symbol,
        "main_contract": "NEAR",
        "main_expiry": "MONTHLY",
        "product_type": "NRML",
        "exit_order_product_type": "",
        "qty_type": "Qty",
        "qty": qty,
        "lot": 1,
        "atm": 0,
        "strike_price": 0,
        "option_type": "",
        "intraday_entry_time": "9:16",
        "intraday_exit_time": "15:25",
        "is_intraday": is_intraday,
        "jobbing_side": jobbing_side,
        "jobbing_start_price": 0,
        "jobbing_end_price": 0,
        "average_by": "Point",
        "average_value": average_value,
        "target_by": "Point",
        "target": 0,
        "intraday_target": intraday_target,
        "maximum_steps": maximum_steps,
        "maximum_target_steps": 0,
        "sqroff_on_maximum_steps": False,
        "calculate_qty_on_market_jump": False,
        "allow_update_parameters": True,
        "order_type": "Market Order",
        "no_of_limit_order_retry": 0,
        "retry_at_every_seconds": 0,
        "market_order_after_retry": False,
        "reset_cycle_by_master_tpsl": False,
        "rollover_before_days": 0,
        "is_auto_rollover": False,
        "rollover_time": "0:0",
        "master_tp_money": 0,
        "master_sl_money": 0,
        "reset_cycle_on_positive_mtm": 0,
        "required_margin": 100000,
        "is_trail_sl": False,
        "profit_move": 0,
        "sl_move": 0,
        "no_of_trail_sl": 0,
        "scalping_opening_qty": 0,
        "increase_qty_on_avg": False,
        "increase_qty": 0,
        "increase_qty_type": None,
        "rebacktest": False,
        "effect_all_sub_strategies": False,
    }

    response = [
        {
            "client_id": 40495,
            "is_deployed": False,
            "id": 416156,
            "execution_level": "Level 1",
        }
    ]

    return {"payload": payload, "response": response, "status": "success"}


@mcp.tool()
def create_scalping_strategy(
    symbol: str,
    averaging_points: int,
    target_points: int,
    max_steps: int = 50,
    quantity: int = 1,
    side: Literal["BUY", "SELL"] = "BUY",
) -> dict:
    """
    Create a scalping strategy for a given symbol.

    Args:
        symbol: Trading symbol (e.g., RELIANCE, INFY)
        averaging_points: Points interval for averaging (e.g., 100)
        target_points: Target profit in points (e.g., 100)
        max_steps: Maximum number of averaging steps (default: 50)
        quantity: Quantity per trade (default: 1)
        side: BUY or SELL (default: BUY)

    Returns:
        Strategy configuration and deployment response
    """

    strategy_name = f"{symbol} Scalping"

    return _build_strategy_payload(
        strategy_name=strategy_name,
        symbol=symbol,
        exchange="NSE",
        segment="EQ",
        qty=quantity,
        average_value=averaging_points,
        intraday_target=target_points,
        maximum_steps=max_steps,
        jobbing_side=side,
        is_intraday=False,
    )


if __name__ == "__main__":
    mcp.run()
