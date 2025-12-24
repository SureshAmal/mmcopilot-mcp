"""
API Request/Response Logger for MCP Tools

Logs all API calls with requests and responses to session-specific files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class APILogger:
    """Logger for API requests and responses."""
    
    def __init__(self, log_dir: str = "logs/api_calls"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_file: Optional[Path] = None
        self.session_id: Optional[str] = None
    
    def set_session(self, session_id: str):
        """Set the current session ID for logging."""
        self.session_id = session_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_file = self.log_dir / f"session_{session_id}_{timestamp}.log"
    
    def log_request(
        self,
        tool_name: str,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None
    ):
        """Log an API request."""
        if not self.current_session_file:
            # Create default session if none set
            self.set_session("default")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "REQUEST",
            "tool_name": tool_name,
            "method": method,
            "url": url,
            "headers": self._sanitize_headers(headers),
            "params": params,
            "json_body": json_body
        }
        
        self._write_log(log_entry)
    
    def log_response(
        self,
        tool_name: str,
        status_code: int,
        url: str,
        response_headers: Dict[str, str],
        response_body: Any,
        error: Optional[str] = None
    ):
        """Log an API response."""
        if not self.current_session_file:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "RESPONSE",
            "tool_name": tool_name,
            "url": url,
            "status_code": status_code,
            "headers": dict(response_headers),
            "body": response_body,
            "error": error
        }
        
        self._write_log(log_entry)
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers."""
        sanitized = headers.copy()
        sensitive_keys = ['authorization', 'bearer', 'api-key', 'x-api-key']
        
        for key in list(sanitized.keys()):
            if key.lower() in sensitive_keys:
                sanitized[key] = "***REDACTED***"
        
        return sanitized
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file."""
        try:
            with open(self.current_session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, indent=2, ensure_ascii=False))
                f.write("\n" + "=" * 80 + "\n")
        except Exception as e:
            logging.error(f"Failed to write API log: {e}")


# Global logger instance
api_logger = APILogger()
