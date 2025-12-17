from fastmcp import FastMCP
from tool_loader import fetch_and_register_tools
import sys
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Mock FastMCP
class MockMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self, name=None, description=None):
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = {
                "description": description,
                "func": func
            }
            print(f"Registered tool: {tool_name}")
            return func
        return decorator

mcp = MockMCP()
fetch_and_register_tools(mcp, "http://dummy", "dummy_token")

if "create_scalping_strategy" in mcp.tools:
    print("SUCCESS: create_scalping_strategy found!")
    tool_func = mcp.tools["create_scalping_strategy"]["func"]
    
    # Test execution with minimal args to see payload and error
    print("\n--- Executing Tool to Debug 400 Error ---")
    try:
        # Using the arguments from the user's request that failed
        result = tool_func(
            strategy_name='Reliance Strategy', 
            main_exchange='NSE', 
            main_segment='EQ', 
            main_symbol='RELIANCE', 
            product_type='CNC', 
            qty_type='Qty', 
            qty=1, 
            is_intraday=True, 
            jobbing_side='BUY', 
            order_type='Market Order', 
            average_by='Point', 
            average_value=10, 
            target_by='Point', 
            target=30
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Execution failed with exception: {e}")
else:
    print("FAILURE: create_scalping_strategy not found.")
