"""
Base API service class for MarketMaya API interactions.

Provides common functionality for making HTTP requests, error handling,
and response processing.
"""

import httpx
import logging
from typing import Optional, Dict, Any, Literal
from abc import ABC

logger = logging.getLogger("mcp_server")


class BaseAPIService(ABC):
    """Base class for all API service classes."""
    
    def __init__(self, base_url: str, auth_headers: Dict[str, str]):
        """
        Initialize the API service.
        
        Args:
            base_url: Base URL for API endpoints
            auth_headers: Authentication headers
        """
        self.base_url = base_url.rstrip('/')
        self.auth_headers = auth_headers
        self.timeout = 30.0
    
    def _make_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (will be appended to base_url)
            **kwargs: Additional arguments to pass to httpx (json, params, etc.)
            
        Returns:
            Parsed JSON response
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        url = f"{self.base_url}{endpoint}"
        
        # Merge auth headers with any custom headers
        headers = self.auth_headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        logger.info(f"Making {method} request to {url}")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                # Check for errors
                if response.status_code != 200:
                    return self._handle_error(response)
                
                # Parse response
                try:
                    return response.json()
                except Exception:
                    # If response is not JSON, return as text
                    return {"text": response.text}
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return self._handle_error(e.response)
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {
                "status": "error",
                "message": f"Request failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def _handle_error(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle error responses from the API.
        
        Args:
            response: HTTP response object
            
        Returns:
            Error dictionary with status and message
        """
        try:
            error_data = response.json()
            error_msg = error_data.get(
                "message",
                error_data.get("error", response.text)
            )
        except Exception:
            error_msg = response.text
        
        logger.error(f"API error ({response.status_code}): {error_msg}")
        
        return {
            "status": "error",
            "message": f"API error ({response.status_code}): {error_msg}",
            "status_code": response.status_code
        }
    
    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, json=json, **kwargs)
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def put(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, json=json, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
