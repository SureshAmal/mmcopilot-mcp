"""
Enhanced dynamic tool loader with validation and improved code generation.

This module fetches tool definitions from an API and dynamically registers them
with the MCP server using proper validation and error handling.
"""

import httpx
import logging
import os
import sys
import json
from typing import Optional, Literal, List, Any, Dict
from fastmcp import FastMCP

from ..models.dynamic_tool import ToolDefinition, APIToolListResponse, ToolParameter
from ..utils.codegen import escape_string_for_python, sanitize_identifier, validate_python_identifier
from ..utils.validation import validate_tool_name, normalize_endpoint


def log_stderr(msg: str):
    """Log a message to stderr for visibility during server startup."""
    sys.stderr.write(f"[ToolLoader] {msg}\n")
    sys.stderr.flush()


def generate_tool_function_code(
    tool_def: ToolDefinition,
    api_base_url: str,
    mcp_var_name: str = "mcp"
) -> str:
    """
    Generate Python code for a dynamic tool function.
    
    Args:
        tool_def: Validated tool definition
        api_base_url: Base URL for API calls
        mcp_var_name: Name of the MCP instance variable
        
    Returns:
        Python code string for the tool function
    """
    tool_name = tool_def.api_name
    description = escape_string_for_python(tool_def.api_description or "")
    endpoint = tool_def.get_endpoint()
    method = tool_def.api_method
    
    # Build function signature
    params = tool_def.get_parameters()
    sig_parts = []
    doc_params = []
    
    for param in params:
        p_name = param.name
        p_type = param.get_python_type()
        p_default = param.get_default_value()
        
        if p_default:
            sig_parts.append(f"{p_name}: {p_type} = {p_default}")
        else:
            sig_parts.append(f"{p_name}: {p_type}")
        
        param_desc = escape_string_for_python(param.description or "")
        doc_params.append(f"        {p_name}: {param_desc}")
    
    sig_str = ", ".join(sig_parts)
    doc_str = "\n".join(doc_params) if doc_params else "        No parameters"
    
    # Normalize endpoint with base URL
    full_url_logic = f'''
    endpoint = "{escape_string_for_python(endpoint)}"
    if not endpoint.startswith("http"):
        base = "{escape_string_for_python(api_base_url)}"
        # Ensure base doesn't end with / and endpoint doesn't start with /
        if base.endswith("/"): 
            base = base[:-1]
        if endpoint.startswith("/"): 
            endpoint = endpoint[1:]
        url = f"{{base}}/{{endpoint}}"
    else:
        url = endpoint
'''
    
    # Generate the function code
    func_code = f'''
@{mcp_var_name}.tool(name="{tool_name}", description="{description}")
def {tool_name}({sig_str}) -> str:
    """
    {tool_def.api_description or 'Dynamic tool'}
    
    Args:
{doc_str}
    
    Returns:
        JSON string with API response
    """
    import httpx
    import json
    from mmcopilot_mcp.config import BEARER_TOKEN
    {full_url_logic}
    
    # Prepare params (filter out internal vars)
    params = locals().copy()
    params.pop("httpx", None)
    params.pop("json", None)
    params.pop("BEARER_TOKEN", None)
    params.pop("endpoint", None)
    params.pop("base", None)
    params.pop("url", None)
    
    # Remove None values for optional params
    params = {{k: v for k, v in params.items() if v is not None}}
    
    headers = {{
        "Authorization": f"Bearer {{BEARER_TOKEN}}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }}
    
    # api_logger is available via exec_globals (no import needed)
    
    try:
        with httpx.Client(timeout=30.0) as client:
            method_upper = "{method}".upper()
            
            # Log request
            api_logger.log_request(
                tool_name="{tool_name}",
                method=method_upper,
                url=url,
                headers=headers,
                params=params if method_upper == "GET" else None,
                json_body=params if method_upper != "GET" else None
            )
            
            if method_upper == "GET":
                response = client.get(url, params=params, headers=headers)
            elif method_upper == "POST":
                response = client.post(url, json=params, headers=headers)
            elif method_upper == "PUT":
                response = client.put(url, json=params, headers=headers)
            elif method_upper == "DELETE":
                response = client.delete(url, json=params, headers=headers)
            elif method_upper == "PATCH":
                response = client.patch(url, json=params, headers=headers)
            else:
                error_msg = f"Unsupported HTTP method: {{method_upper}}"
                api_logger.log_response(
                    tool_name="{tool_name}",
                    status_code=0,
                    url=url,
                    response_headers={{}},
                    response_body=None,
                    error=error_msg
                )
                return json.dumps({{"error": error_msg}})
            
            # Log response
            try:
                response_body = response.json() if response.content else None
            except:
                response_body = response.text if response.content else None
            
            api_logger.log_response(
                tool_name="{tool_name}",
                status_code=response.status_code,
                url=url,
                response_headers=dict(response.headers),
                response_body=response_body,
                error=None if response.status_code < 400 else f"HTTP {{response.status_code}}"
            )
            
            response.raise_for_status()
            
            # Check if response is empty
            if not response.content:
                return json.dumps({{"error": "Empty response from API"}})
            
            try:
                return json.dumps(response.json())
            except json.JSONDecodeError:
                return json.dumps({{"error": "Invalid JSON response", "text": response.text[:500]}})
                
    except httpx.HTTPStatusError as e:
        # Log HTTP error
        api_logger.log_response(
            tool_name="{tool_name}",
            status_code=e.response.status_code,
            url=str(e.request.url),
            response_headers=dict(e.response.headers),
            response_body=e.response.text[:500],
            error=f"HTTP {{e.response.status_code}}"
        )
        return json.dumps({{"error": f"HTTP {{e.response.status_code}}", "message": e.response.text[:500]}})
    except Exception as e:
        # Log general error
        api_logger.log_response(
            tool_name="{tool_name}",
            status_code=0,
            url=url,
            response_headers={{}},
            response_body=None,
            error=str(e)
        )
        return json.dumps({{"error": "Request failed", "message": str(e)}})
'''
    
    return func_code


def register_single_tool(
    mcp: FastMCP,
    tool_def: ToolDefinition,
    api_base_url: str,
    log_file: Optional[str] = None
) -> bool:
    """
    Register a single dynamic tool with proper error handling.
    
    Args:
        mcp: FastMCP instance
        tool_def: Validated tool definition
        api_base_url: Base URL for API calls
        log_file: Optional path to log generated code
        
    Returns:
        True if registration succeeded, False otherwise
    """
    tool_name = tool_def.api_name
    
    try:
        # Validate tool name
        if not validate_tool_name(tool_name):
            sanitized_name = sanitize_identifier(tool_name)
            log_stderr(f"Warning: Tool name '{tool_name}' is invalid, using '{sanitized_name}'")
            tool_def.api_name = sanitized_name
            tool_name = sanitized_name
        
        # Generate function code
        func_code = generate_tool_function_code(tool_def, api_base_url)
        
        # Log generated code if log file provided
        if log_file:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n{'='*80}\n")
                    f.write(f"# Tool: {tool_name}\n")
                    f.write(f"# Endpoint: {tool_def.get_endpoint()}\n")
                    f.write(f"# Method: {tool_def.api_method}\n")
                    f.write(f"{'='*80}\n")
                    f.write(func_code)
            except Exception as e:
                log_stderr(f"Warning: Failed to log code for {tool_name}: {e}")
        
        # Prepare execution context
        from .api_logger import api_logger
        
        exec_globals = {
            "mcp": mcp,
            "Optional": Optional,
            "Literal": Literal,
            "List": List,
            "Any": Any,
            "Dict": Dict,
            "dict": dict,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "api_logger": api_logger,  # Make api_logger available to generated functions
        }
        
        # Execute the generated code
        exec(func_code, exec_globals)
        
        log_stderr(f"✅ Registered tool: {tool_name}")
        return True
        
    except SyntaxError as e:
        log_stderr(f"❌ Syntax error in generated code for '{tool_name}': {e}")
        log_stderr(f"   Line {e.lineno}: {e.text}")
        return False
        
    except Exception as e:
        log_stderr(f"❌ Failed to register tool '{tool_name}': {e}")
        import traceback
        log_stderr(f"   Traceback: {traceback.format_exc()}")
        return False


def fetch_and_register_tools(mcp: FastMCP, api_base_url: str, bearer_token: str):
    """
    Fetch tool definitions from API and register them dynamically.
    
    Args:
        mcp: FastMCP instance to register tools with
        api_base_url: Base URL for tool API calls
        bearer_token: Bearer token for authentication (used for tool calls)
    """
    # Use FETCH_BEARER_TOKEN for fetching the tool definitions
    fetch_token = os.getenv("FETCH_BEARER_TOKEN")
    
    # Debug: Show what we got
    log_stderr(f"🔍 Debug: .env loaded from config module")
    log_stderr(f"🔍 FETCH_BEARER_TOKEN present: {bool(fetch_token)}")
    if fetch_token:
        log_stderr(f"🔍 Token length: {len(fetch_token)} chars, starts with: {fetch_token[:20]}...")
    
    if not fetch_token:
        log_stderr("❌ FETCH_BEARER_TOKEN not set, skipping dynamic tool loading")
        return
    
    url = "https://webapi.marketmaya.com/api/AiRestApiMaster/GetAIRestApiList?Skip=0&Take=20&OrderBy=id&Filter=&OrderDirection=1&ColumnFilters=%7B%7D&wlId=1"
    
    headers = {
        "Authorization": f"Bearer {fetch_token}",
        "Content-Type": "application/json"
    }
    
    try:
        log_stderr(f"📥 Fetching dynamic tools from API...")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            
            if response.status_code != 200:
                log_stderr(f"❌ Failed to fetch tools: HTTP {response.status_code}")
                log_stderr(f"   Response: {response.text[:200]}")
                return
            
            data = response.json()
            
            # Parse response using Pydantic model
            try:
                api_response = APIToolListResponse(data=data.get("data", {}))
                tools_list = api_response.get_tool_list()
            except Exception as e:
                log_stderr(f"❌ Failed to parse API response: {e}")
                log_stderr(f"   Response structure: {list(data.keys())}")
                return
            
            log_stderr(f"📋 Found {len(tools_list)} tool definitions")
            
            if not tools_list:
                log_stderr("⚠️  No valid tools found to register")
                return
            
            # Setup log file for generated code
            log_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "logs"
            )
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "generated_tools.log")
            
            # Clear previous log
            try:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"# Generated Dynamic Tools\n")
                    f.write(f"# Generated at: {__import__('datetime').datetime.now()}\n")
                    f.write(f"# Total tools: {len(tools_list)}\n")
            except Exception as e:
                log_stderr(f"Warning: Could not create log file: {e}")
                log_file = None
            
            # Register each tool
            success_count = 0
            failed_count = 0
            
            for tool_def in tools_list:
                if register_single_tool(mcp, tool_def, api_base_url, log_file):
                    success_count += 1
                else:
                    failed_count += 1
            
            # Summary
            log_stderr(f"\n{'='*60}")
            log_stderr(f"📊 Dynamic Tool Registration Summary:")
            log_stderr(f"   ✅ Successful: {success_count}")
            log_stderr(f"   ❌ Failed: {failed_count}")
            log_stderr(f"   📝 Generated code logged to: {log_file}")
            log_stderr(f"{'='*60}\n")
            
    except httpx.TimeoutException:
        log_stderr("❌ Timeout while fetching dynamic tools")
    except httpx.RequestError as e:
        log_stderr(f"❌ Network error while fetching tools: {e}")
    except Exception as e:
        log_stderr(f"❌ Unexpected error in fetch_and_register_tools: {e}")
        import traceback
        log_stderr(f"   Traceback: {traceback.format_exc()}")
