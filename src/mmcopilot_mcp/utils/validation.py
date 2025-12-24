"""Validation utilities for tool definitions and parameters."""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> str:
    """
    Validate and normalize a URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Normalized URL
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")
    
    url = url.strip()
    
    # If it's a relative path, allow it
    if url.startswith('/'):
        return url
    
    # If it's a full URL, validate it
    try:
        result = urlparse(url)
        
        # Check if it has a scheme (http/https)
        if result.scheme and result.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {result.scheme}. Must be http or https")
        
        return url
    except Exception as e:
        raise ValueError(f"Invalid URL: {url}. Error: {e}")


def is_valid_http_method(method: str) -> bool:
    """
    Check if a string is a valid HTTP method.
    
    Args:
        method: HTTP method to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    return method.upper() in valid_methods


def validate_tool_name(name: str) -> bool:
    """
    Validate a tool name is suitable for use as a Python function name.
    
    Args:
        name: Tool name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False
    
    # Must be a valid Python identifier
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return False
    
    # Cannot be a Python keyword
    python_keywords = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    }
    
    if name in python_keywords:
        return False
    
    return True


def normalize_endpoint(base_url: str, endpoint: str) -> str:
    """
    Normalize an endpoint by combining it with a base URL if needed.
    
    Args:
        base_url: Base URL
        endpoint: Endpoint path
        
    Returns:
        Complete URL
    """
    # If endpoint is already a full URL, return it
    if endpoint.startswith('http://') or endpoint.startswith('https://'):
        return endpoint
    
    # Remove trailing slash from base
    base_url = base_url.rstrip('/')
    
    # Ensure endpoint starts with /
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    
    return f"{base_url}{endpoint}"
