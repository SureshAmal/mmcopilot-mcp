import httpx
import logging
import os
import sys
import json
from typing import Optional, Literal, List, Any
from fastmcp import FastMCP
from ..server import logger

def log_stderr(msg):
    sys.stderr.write(f"[ToolLoader] {msg}\n")
    sys.stderr.flush()

def get_python_type(param_def):
    p_type = param_def.get("type")
    is_required = param_def.get("required", False)
    
    py_type = "Any"
    if p_type == "string":
        py_type = "str"
    elif p_type == "integer":
        py_type = "int"
    elif p_type == "number":
        py_type = "float"
    elif p_type == "boolean":
        py_type = "bool"
    elif p_type == "array":
        py_type = "list"
    elif p_type == "object":
        py_type = "dict"
    
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
            
            log_stderr(f"Found {len(tools_list)} tools to register.")

            for tool_def in tools_list:
                try:
                    # Extract details from flat fields or requestJson
                    tool_name = tool_def.get("apiName")
                    description = tool_def.get("apiDescription")
                    api_endpoint = tool_def.get("apiEndpoint") or tool_def.get("endPointUrl")
                    if api_endpoint:
                        api_endpoint = api_endpoint.strip()
                    method = tool_def.get("apiMethod") or tool_def.get("apiType") or "GET"
                    params = []

                    # Try parsing requestJson for metadata and params
                    req_json_str = tool_def.get("requestJson")
                    if req_json_str:
                        try:
                            req_data = json.loads(req_json_str)
                            if not tool_name:
                                tool_name = req_data.get("tool_name")
                            if not description:
                                description = req_data.get("description")
                            
                            # Params might be in 'inputs' in requestJson
                            if "inputs" in req_data:
                                params = req_data["inputs"]
                        except Exception as e:
                            log_stderr(f"Failed to parse requestJson: {e}")

                    if not tool_name:
                        log_stderr(f"Skipping tool with no name: {tool_def}")
                        continue
                        
                    if not description:
                        description = "No description provided"
                    
                    # If params not found in requestJson, try apiParams
                    if not params:
                        params_json = tool_def.get("apiParams", "[]")
                        try:
                            params = json.loads(params_json) if isinstance(params_json, str) else params_json
                        except json.JSONDecodeError:
                            log_stderr(f"Failed to parse params for {tool_name}")
                            params = []

                    # Build function signature
                    sig_parts = []
                    doc_params = []
                    
                    for param in params:
                        p_name = param.get("name")
                        p_type = get_python_type(param)
                        p_default = get_default_value(param)
                        
                        if p_default:
                            sig_parts.append(f"{p_name}: {p_type} = {p_default}")
                        else:
                            sig_parts.append(f"{p_name}: {p_type}")
                            
                        doc_params.append(f"    {p_name}: {param.get('description', '')}")

                    sig_str = ", ".join(sig_parts)
                    doc_str = "\n".join(doc_params)
                    
                    # Create function code
                    func_code = f"""
@mcp.tool(name="{tool_name}", description="{description}")
def {tool_name}({sig_str}) -> str:
    '''
    {description}
    
    Args:
{doc_str}
    '''
    import httpx
    import json
    import os
    
    # Construct URL
    endpoint = "{api_endpoint}"
    if not endpoint.startswith("http"):
        base = "{api_base_url}"
        # Ensure base doesn't end with / and endpoint doesn't start with /
        if base.endswith("/"): base = base[:-1]
        if endpoint.startswith("/"): endpoint = endpoint[1:]
        url = f"{{base}}/{{endpoint}}"
    else:
        url = endpoint
        
    # Prepare params
    params = locals().copy()
    # Remove internal vars
    params.pop("httpx", None)
    params.pop("json", None)
    params.pop("os", None)
    
    headers = {{
        "Authorization": f"Bearer {{os.getenv('BEARER_TOKEN')}}",
        "Content-Type": "application/json"
    }}
    
    try:
        with httpx.Client() as client:
            if "{method}".upper() == "GET":
                response = client.get(url, params=params, headers=headers)
            else:
                response = client.post(url, json=params, headers=headers)
            
            # Check if response is empty
            if not response.content:
                return "Error: Empty response from API"
                
            try:
                return json.dumps(response.json())
            except json.JSONDecodeError:
                return f"Error executing {tool_name}: {{response.text}}"
    except Exception as e:
        return f"Error executing {tool_name}: {{str(e)}}"
"""
                    # Log generated code to file
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    log_file = os.path.join(log_dir, "generated_tools.log")
                    
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"\n\n# ================= {tool_name} =================\n")
                        f.write(func_code)
                        
                    log_stderr(f"Logged generated code for {tool_name} to {log_file}")

                    # Execute dynamic code
                    # We need to pass 'mcp' to the exec context
                    exec_globals = {
                        "mcp": mcp,
                        "Optional": Optional,
                        "Literal": Literal,
                        "List": List,
                        "Any": Any,
                        "dict": dict
                    }
                    exec(func_code, exec_globals)
                    log_stderr(f"Registered tool: {tool_name}")
                    
                except Exception as e:
                    log_stderr(f"Failed to register tool {tool_def.get('apiName')}: {e}")
                    logger.error(f"Failed to register tool {tool_def.get('apiName')}: {e}")

    except Exception as e:
        log_stderr(f"Error in fetch_and_register_tools: {e}")
        logger.error(f"Error in fetch_and_register_tools: {e}")
