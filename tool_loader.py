import httpx
import json
import logging
import os
import sys
from typing import Optional, Literal, List, Any, get_type_hints
from fastmcp import FastMCP
import inspect

logger = logging.getLogger("mcp_server")

def log_stderr(msg):
    sys.stderr.write(f"[ToolLoader] {msg}\n")
    sys.stderr.flush()

def get_python_type(param_def):
    p_type = param_def.get("type")
    is_required = param_def.get("required", False)
    
    py_type = "str"
    if p_type == "integer":
        py_type = "int"
    elif p_type == "number":
        py_type = "float"
    elif p_type == "boolean":
        py_type = "bool"
    elif p_type == "array":
        py_type = "list"
    
    # Handle Enums
    if "enum" in param_def and param_def["enum"]:
        options = param_def["enum"]
        # Ensure options are strings for Literal
        options_str = ", ".join([f"'{opt}'" for opt in options])
        py_type = f"Literal[{options_str}]"
    
    if not is_required:
        py_type = f"Optional[{py_type}]"
        
    return py_type

def get_default_value(param_def):
    # Check if default is explicitly provided in the definition
    if "default" in param_def:
        default = param_def.get("default")
        if default is None:
            return "None"
        if isinstance(default, str):
            return f"'{default}'"
        return str(default)
        
    # If no default provided but not required, assume None
    if not param_def.get("required", False):
        return "None"
        
    return None

def fetch_and_register_tools(mcp: FastMCP, api_base_url: str, bearer_token: str):
    # Use FETCH_BEARER_TOKEN for fetching the tool definitions
    fetch_token = os.getenv("FETCH_BEARER_TOKEN")
    url = "https://webapi.marketmaya.com/api/AiRestApiMaster/GetAIRestApiList?Skip=0&Take=20&OrderBy=id&Filter=&OrderDirection=1&ColumnFilters=%7B%7D&wlId=1"
    
    headers = {
        "Authorization": f"Bearer {fetch_token}",
        "Content-Type": "application/json"
    }
    
    try:
        log_stderr(f"Fetching dynamic tools from {url}")
        
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=10.0)
            if response.status_code != 200:
                log_stderr(f"Failed to fetch tools: {response.status_code} {response.text}")
                logger.error(f"Failed to fetch tools: {response.status_code} {response.text}")
                return

            data = response.json()
            log_stderr(f"Fetched tools data: {str(data)[:100]}...")
            
            # Navigate to the list
            # Structure: { "data": { "aiRestApiList": [ ... ] } }
            response_data = data.get("data", {})
            
            if isinstance(response_data, list):
                if not response_data:
                    log_stderr("Warning: API returned empty list for 'data' field. No tools found.")
                    tools_list = []
                else:
                    log_stderr(f"Warning: 'data' field is a list, expected dict. Content: {str(response_data)[:100]}...")
                    tools_list = []
            elif isinstance(response_data, dict):
                tools_list = response_data.get("aiRestApiList", [])
            else:
                log_stderr(f"Warning: 'data' field is of type {type(response_data)}, expected dict.")
                tools_list = []

        log_stderr(f"Found {len(tools_list)} tools in response")
        
        for tool_item in tools_list:
            try:
                register_single_tool(mcp, tool_item, bearer_token)
            except Exception as e:
                log_stderr(f"Error registering tool {tool_item.get('id')}: {e}")
                logger.error(f"Error registering tool {tool_item.get('id')}: {e}")

    except Exception as e:
        log_stderr(f"Exception in fetch_and_register_tools: {e}")
        logger.error(f"Exception in fetch_and_register_tools: {e}")

def register_single_tool(mcp: FastMCP, tool_item: dict, bearer_token: str):
    request_json_str = tool_item.get("requestJson")
    if not request_json_str:
        return

    tool_def = json.loads(request_json_str)
    tool_name = tool_def.get("tool_name")
    description = tool_def.get("description", "")
    inputs = tool_def.get("inputs", [])
    endpoint_url = tool_item.get("endPointUrl")
    method = tool_item.get("apiType", "POST")

    if not tool_name or not endpoint_url:
        return

    # Build function signature dynamically
    params_code = []
    args_mapping = []
    
    # Sort inputs: required first, then optional
    sorted_inputs = sorted(inputs, key=lambda x: not x.get("required", False))

    for inp in sorted_inputs:
        p_name = inp["name"]
        p_type = get_python_type(inp)
        p_default = get_default_value(inp)
        
        param_str = f"{p_name}: {p_type}"
        if p_default is not None:
            param_str += f" = {p_default}"
        
        params_code.append(param_str)
        args_mapping.append(p_name)

    sig_str = ", ".join(params_code)
    
    # Define the function code
    func_code = f"""
@mcp.tool(name="{tool_name}", description="{description}")
def {tool_name}({sig_str}):
    '''{description}'''
    import httpx
    import json
    import os
    
    url = "{endpoint_url}"
    method = "{method}"
    token = os.getenv("BEARER_TOKEN", "")
    
    # Collect arguments
    payload = {{}}
    local_vars = locals()
    args_list = {args_mapping}
    
    for arg in args_list:
        if arg in local_vars:
            val = local_vars[arg]
            # Filter out None values to avoid sending nulls for optional fields
            if val is not None:             
                payload[arg] = val
            
    # Log the payload for debugging
    print(f"[Tool: {tool_name}] Payload: {{json.dumps(payload, indent=2)}}")

    headers = {{
        "Authorization": f"Bearer {{token}}",
        "Content-Type": "application/json"
    }}
    
    try:
        with httpx.Client() as client:
            m = method.upper()
            if m == "POST":
                resp = client.post(url, json=payload, headers=headers, timeout=30.0)
            elif m == "PUT":
                resp = client.put(url, json=payload, headers=headers, timeout=30.0)
            elif m == "DELETE":
                resp = client.delete(url, params=payload, headers=headers, timeout=30.0)
            else:
                # GET and others
                resp = client.get(url, params=payload, headers=headers, timeout=30.0)
                
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        return f"Error executing {tool_name}: {{e.response.status_code}} {{e.response.text}}"
    except Exception as e:
        return f"Error executing {tool_name}: {{str(e)}}"
"""
    
    # Execute the code to create the function
    local_scope = {}
    global_scope = {
        "Optional": Optional,
        "Literal": Literal,
        "List": List,
        "Any": Any,
        "httpx": httpx,
        "json": json,
        "mcp": mcp
    }
    
    # Debug: Print generated code
    print(f"\n--- Generated Code for {tool_name} ---")
    print(func_code)
    print("--------------------------------------\n")

    exec(func_code, global_scope, local_scope)
    
    # func = local_scope[tool_name]
    
    # Register with MCP
    # The decorator @mcp.tool() inside exec() handles registration
    # mcp.tool(name=tool_name, description=description)(func)
    log_stderr(f"Registered dynamic tool: {tool_name}")
    logger.info(f"Registered dynamic tool: {tool_name}")

