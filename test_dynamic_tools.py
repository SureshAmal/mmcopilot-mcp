import json
import logging
from unittest.mock import MagicMock, patch
from fastmcp import FastMCP
from tool_loader import fetch_and_register_tools

# Mock data provided by the user
MOCK_API_RESPONSE = {
    "statusCode": 200,
    "message": "Success",
    "data": {
        "aiRestApiList": [
            {
                "id": "AW92uaWrkQaA0$KULZeBfmTkAaC0$aC0$",
                "wlId": "AW92uaWrkQaA0$KULZeBfmTkAaC0$aC0$",
                "apiType": "POST",
                "endPointUrl": "https://api.marketmaya.com/api/mainStrategy/createScalpingStrategy",
                "requestJson": json.dumps({
  "tool_name": "create_scalping_strategy",
  "description": "scalping strategy creation tool",
  "version": "1.0",
  "inputs": [
    {
      "name": "id",
      "type": "string",
      "required": False,
      "default": "",
      "description": "Unique ID of the strategy"
    },
    {
      "name": "strategy_name",
      "type": "string",
      "required": True,
      "default": "",
      "description": "Name of the strategy"
    },
    {
      "name": "short_description",
      "type": "string",
      "required": False,
      "default": "",
      "description": "Short summary for UI"
    },
    {
      "name": "long_description",
      "type": "string",
      "required": False,
      "default": None,
      "description": "Detailed description"
    },
    {
      "name": "strategy_id",
      "type": "string",
      "required": False,
      "default": "",
      "description": "Internal strategy ID"
    },
    {
      "name": "mix_name",
      "type": "string",
      "required": False,
      "default": "",
      "description": "Name of the mix"
    },
    {
      "name": "main_exchange",
      "type": "string",
      "required": True,
      "enum": [
        "NSE",
        "NFO",
        "BFO",
        "BSE",
        "MCX",
        "CDS"
      ],
      "default": "NFO",
      "description": "Exchange for execution"
    },
    {
      "name": "main_segment",
      "type": "string",
      "required": True,
      "enum": [
        "FUT",
        "OPT",
        "EQ"
      ],
      "default": "FUT",
      "description": "Trading segment"
    },
    {
      "name": "main_symbol",
      "type": "string",
      "required": True,
      "default": "",
      "description": "Trading symbol"
    },
    {
      "name": "main_contract",
      "type": "string",
      "required": False,
      "enum": [
        "NEAR",
        "NEXT",
        "FAR"
      ],
      "default": "NEAR",
      "description": "Contract selection"
    },
    {
      "name": "main_expiry",
      "type": "string",
      "required": False,
      "enum": [
        "WEEKLY",
        "MONTHLY"
      ],
      "default": "MONTHLY",
      "description": "Expiry cycle"
    },
    {
      "name": "product_type",
      "type": "string",
      "required": True,
      "enum": [
        "MIS",
        "NRML",
        "CNC",
        "MTF"
      ],
      "default": "MIS",
      "description": "Broker product type"
    },
    {
      "name": "exit_order_product_type",
      "type": "string",
      "required": False,
      "default": "",
      "description": "Product type for exit orders"
    },
    {
      "name": "qty_type",
      "type": "string",
      "required": True,
      "enum": [
        "Qty",
        "Lot"
      ],
      "default": "Lot",
      "description": "Quantity calculation type"
    },
    {
      "name": "qty",
      "type": "integer",
      "required": True,
      "default": 1,
      "description": "Base quantity"
    },
    {
      "name": "lot",
      "type": "integer",
      "required": False,
      "default": 1,
      "description": "Lot size if applicable"
    },
    {
      "name": "atm",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "ATM value for options"
    },
    {
      "name": "strike_price",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Strike price for option"
    },
    {
      "name": "option_type",
      "type": "string",
      "required": False,
      "enum": [
        "CALL",
        "PUT"
      ],
      "default": "CALL",
      "description": "Option type"
    },
    {
      "name": "intraday_entry_time",
      "type": "string",
      "required": False,
      "default": "09:15",
      "pattern": "^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]$",
      "description": "Intraday entry time"
    },
    {
      "name": "intraday_exit_time",
      "type": "string",
      "required": False,
      "default": "15:15",
      "pattern": "^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]$",
      "description": "Intraday exit time"
    },
    {
      "name": "is_intraday",
      "type": "boolean",
      "required": True,
      "default": True,
      "description": "Whether the strategy is intraday"
    },
    {
      "name": "jobbing_side",
      "type": "string",
      "required": True,
      "enum": [
        "BUY",
        "SELL"
      ],
      "default": "BUY",
      "description": "Jobbing direction"
    },
    {
      "name": "jobbing_start_price",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Price to start jobbing"
    },
    {
      "name": "jobbing_end_price",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Price to stop averaging"
    },
    {
      "name": "average_by",
      "type": "string",
      "required": False,
      "enum": [
        "Point",
        "Percentage"
      ],
      "default": "Point",
      "description": "Averaging method"
    },
    {
      "name": "average_value",
      "type": "number",
      "required": False,
      "default": 100,
      "description": "Distance between averaging steps"
    },
    {
      "name": "target_by",
      "type": "string",
      "required": False,
      "enum": [
        "Point",
        "Percentage"
      ],
      "default": "Point",
      "description": "Target calculation method"
    },
    {
      "name": "target",
      "type": "number",
      "required": False,
      "default": 100,
      "description": "Per-step target"
    },
    {
      "name": "intraday_target",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Target for intraday"
    },
    {
      "name": "maximum_steps",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Maximum averaging steps"
    },
    {
      "name": "maximum_target_steps",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Max positive-side steps"
    },
    {
      "name": "sqroff_on_maximum_steps",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Square off on max steps"
    },
    {
      "name": "calculate_qty_on_market_jump",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Handle market jump"
    },
    {
      "name": "allow_update_parameters",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Allow updating parameters"
    },
    {
      "name": "order_type",
      "type": "string",
      "required": True,
      "enum": [
        "Market Order",
        "Limit Order"
      ],
      "default": "Market Order",
      "description": "Order execution type"
    },
    {
      "name": "no_of_limit_order_retry",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Number of retry attempts for limit orders"
    },
    {
      "name": "retry_at_every_seconds",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Retry interval in seconds"
    },
    {
      "name": "market_order_after_retry",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Use market order after retry"
    },
    {
      "name": "reset_cycle_by_master_tpsl",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Reset cycle on master TP/SL"
    },
    {
      "name": "rollover_before_days",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Days before expiry to rollover"
    },
    {
      "name": "is_auto_rollover",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Enable auto rollover"
    },
    {
      "name": "is_add_hedge_leg",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Add hedge leg"
    },
    {
      "name": "rollover_time",
      "type": "string",
      "required": False,
      "default": "15:15",
      "pattern": "^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]$",
      "description": "Rollover execution time"
    },
    {
      "name": "master_tp_money",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Master TP money"
    },
    {
      "name": "master_sl_money",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Master SL money"
    },
    {
      "name": "reset_cycle_on_positive_mtm",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Reset cycle after positive MTM"
    },
    {
      "name": "required_margin",
      "type": "number",
      "required": False,
      "default": 1,
      "description": "Estimated margin required"
    },
    {
      "name": "is_trail_sl",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Enable trailing SL"
    },
    {
      "name": "profit_move",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "Profit move for trailing SL"
    },
    {
      "name": "sl_move",
      "type": "number",
      "required": False,
      "default": 0,
      "description": "SL move for trailing SL"
    },
    {
      "name": "no_of_trail_sl",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Number of trailing SL"
    },
    {
      "name": "scalping_opening_qty",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Opening quantity for scalping"
    },
    {
      "name": "increase_qty_on_avg",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Increase quantity on averaging"
    },
    {
      "name": "increase_qty",
      "type": "integer",
      "required": False,
      "default": 0,
      "description": "Quantity increment"
    },
    {
      "name": "increase_qty_type",
      "type": "string",
      "required": False,
      "default": None,
      "description": "Type of quantity increment"
    },
    {
      "name": "rebacktest",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Re-run backtest"
    },
    {
      "name": "sub",
      "type": "array",
      "required": False,
      "default": [],
      "description": "Sub-strategies array"
    },
    {
      "name": "effect_all_sub_strategies",
      "type": "boolean",
      "required": False,
      "default": False,
      "description": "Apply to all sub-strategies"
    }
  ]
}),
                "responseJson": "[]",
                "wlName": "Market Maya",
                "entryDateTime": "2025-12-15T17:56:58.277",
                "entryById": "k2OvPIQj02raB0$uPQCaB0$aB0$E4DAaC0$aC0$"
            }
        ],
        "totalRecords": 1
    }
}

def test_dynamic_tool_creation():
    # Create a fresh FastMCP instance for testing
    mcp = FastMCP("Test MCP")
    
    print("Setting up mock API response...")
    
    # Mock httpx.Client to return our mock response
    with patch("httpx.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.__enter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_client.get.return_value = mock_response
        
        print("Fetching and registering tools...")
        fetch_and_register_tools(mcp, "http://mock-api", "mock-token")
        
        print("\n--- Debugging FastMCP Object ---")
        # print(dir(mcp)) 
        
        # Try to find where tools are stored. 
        # FastMCP likely has a registry. 
        # Based on common patterns, it might be in _tool_registry or similar if _tools failed.
        # Let's try to list tools using the MCP protocol method if possible, 
        # or just inspect the object attributes.
        
        if hasattr(mcp, "_tool_manager"):
             print("Found _tool_manager")
             tools = mcp._tool_manager._tools
        elif hasattr(mcp, "tools"):
             print("Found tools list/dict")
             tools = mcp.tools
        else:
             print("Could not find tools container directly. Printing attributes:")
             print([d for d in dir(mcp) if not d.startswith('__')])
             return

        print("\n--- Registered Tools ---")
        # If tools is a list (FastMCP might store them as list of Tool objects)
        if isinstance(tools, list):
            for tool in tools:
                print(f"Tool Name: {tool.name}")
                print(f"Description: {tool.description}")
                # Parameters might be in tool.parameters or similar
                print("-" * 30)
        # If tools is a dict
        elif isinstance(tools, dict):
            for name, tool in tools.items():
                print(f"Tool Name: {name}")
                # Check if tool is a function or a Tool object
                if hasattr(tool, "description"):
                     print(f"Description: {tool.description}")
                if hasattr(tool, "fn"):
                    import inspect
                    sig = inspect.signature(tool.fn)
                    for param_name, param in sig.parameters.items():
                        print(f"  - {param_name}: {param.annotation} (Default: {param.default})")
                print("-" * 30)

if __name__ == "__main__":
    test_dynamic_tool_creation()
