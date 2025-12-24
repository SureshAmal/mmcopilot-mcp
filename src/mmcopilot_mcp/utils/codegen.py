"""Code generation utilities for creating dynamic tool functions."""

import re
from typing import Any


def escape_string_for_python(s: str) -> str:
    """
    Escape a string to be safely embedded in Python code.
    
    Args:
        s: String to escape
        
    Returns:
        Escaped string safe for use in Python string literals
    """
    if not s:
        return ""
    
    # Replace backslashes first (to avoid double-escaping)
    s = s.replace("\\", "\\\\")
    
    # Escape quotes
    s = s.replace('"', '\\"')
    s = s.replace("'", "\\'")
    
    # Escape other special characters
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")
    
    return s


def format_python_value(value: Any) -> str:
    """
    Convert a Python value to its string representation for code generation.
    
    Args:
        value: Python value to convert
        
    Returns:
        String representation suitable for Python code
    """
    if value is None:
        return "None"
    elif isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, str):
        escaped = escape_string_for_python(value)
        return f'"{escaped}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (list, tuple)):
        items = [format_python_value(item) for item in value]
        return f"[{', '.join(items)}]"
    elif isinstance(value, dict):
        items = [f'"{k}": {format_python_value(v)}' for k, v in value.items()]
        return f"{{{', '.join(items)}}}"
    else:
        return repr(value)


def validate_python_identifier(name: str) -> bool:
    """
    Check if a string is a valid Python identifier.
    
    Args:
        name: String to validate
        
    Returns:
        True if valid identifier, False otherwise
    """
    if not name:
        return False
    
    # Check if it matches Python identifier rules
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


def sanitize_identifier(name: str) -> str:
    """
    Convert a string to a valid Python identifier.
    
    Args:
        name: String to sanitize
        
    Returns:
        Valid Python identifier
    """
    if not name:
        return "unnamed_tool"
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"tool_{sanitized}"
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Strip leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    if not sanitized:
        return "unnamed_tool"
    
    return sanitized


def indent_code(code: str, spaces: int = 4) -> str:
    """
    Indent code by a specified number of spaces.
    
    Args:
        code: Code to indent
        spaces: Number of spaces to indent
        
    Returns:
        Indented code
    """
    indent = " " * spaces
    lines = code.split("\n")
    return "\n".join(indent + line if line.strip() else line for line in lines)
