"""
Pydantic models for validating dynamic tool definitions from API responses.
"""
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
import json


class ToolParameter(BaseModel):
    """Model for a tool parameter definition."""
    
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, integer, number, boolean, array, object)")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value")
    enum: Optional[List[Any]] = Field(None, description="Allowed values for enum/Literal types")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate parameter type is supported."""
        valid_types = {'string', 'integer', 'number', 'boolean', 'array', 'object', 'list'}
        v_lower = v.lower()
        if v_lower not in valid_types:
            raise ValueError(f"Invalid parameter type: {v}. Must be one of {valid_types}")
        # Normalize 'list' to 'array' for consistency
        if v_lower == 'list':
            return 'array'
        return v_lower
    
    def get_python_type(self) -> str:
        """Convert JSON Schema type to Python type hint."""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict'
        }
        
        base_type = type_mapping.get(self.type, 'Any')
        
        # Handle enum/Literal types
        if self.enum:
            # Ensure enum values are strings for Literal
            enum_values = [f"'{val}'" if isinstance(val, str) else str(val) for val in self.enum]
            base_type = f"Literal[{', '.join(enum_values)}]"
        
        # Add Optional wrapper if not required
        if not self.required:
            return f"Optional[{base_type}]"
        
        return base_type
    
    def get_default_value(self) -> Optional[str]:
        """Get the default value as a Python code string."""
        if self.default is not None:
            if isinstance(self.default, str):
                # Escape quotes in string defaults
                escaped = self.default.replace("'", "\\'").replace('"', '\\"')
                return f"'{escaped}'"
            elif isinstance(self.default, bool):
                return str(self.default)  # Python True/False
            else:
                return str(self.default)
        
        # If not required and no default, use None
        if not self.required:
            return "None"
        
        return None


class ToolDefinition(BaseModel):
    """Model for a complete tool definition from API."""
    
    model_config = {"populate_by_name": True}
    
    api_name: Optional[str] = Field(None, alias="apiName", description="Tool/function name")
    api_type: Optional[str] = Field(None, alias="apiType", description="Tool type/name from API")
    api_description: Optional[str] = Field(None, alias="apiDescription", description="Tool description")
    api_endpoint: Optional[str] = Field(None, alias="apiEndpoint", description="API endpoint URL")
    endpoint_url: Optional[str] = Field(None, alias="endPointUrl", description="Alternative endpoint field")
    call_type: Optional[str] = Field(None, alias="callType", description="HTTP method (GET/POST/etc.)")
    api_method: Optional[str] = Field("GET", alias="apiMethod", description="Alternative HTTP method field")
    api_params: Optional[str] = Field(None, alias="apiParams", description="Parameters as JSON string")
    request_json: Optional[str] = Field(None, alias="requestJson", description="Alternative params field")
    
    @model_validator(mode='after')
    def validate_and_normalize(self) -> 'ToolDefinition':
        """Validate and normalize tool definition fields."""
        
        # Try to extract tool name from multiple sources
        if not self.api_name:
            # First try apiType which contains the tool name in your API
            if self.api_type:
                self.api_name = self.api_type
            # Then try requestJson
            elif self.request_json:
                try:
                    req_data = json.loads(self.request_json)
                    self.api_name = req_data.get("tool_name") or req_data.get("name")
                except Exception:
                    pass
        
        # If still no name, this tool definition is invalid
        if not self.api_name:
            raise ValueError("Tool must have either apiName, apiType, or tool_name in requestJson")
        
        # Ensure we have an endpoint
        if not self.api_endpoint and not self.endpoint_url:
            raise ValueError("Tool must have either apiEndpoint or endPointUrl")
        
        # Use endpoint_url as fallback
        if not self.api_endpoint:
            self.api_endpoint = self.endpoint_url
        
        # Determine HTTP method from callType first, then api_method
        if not self.api_method or self.api_method == "GET":
            if self.call_type:
                self.api_method = self.call_type
        
        if not self.api_method:
            self.api_method = "GET"
        
        # Normalize method to uppercase
        self.api_method = self.api_method.upper()
        
        # Validate HTTP method
        valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}
        if self.api_method not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {self.api_method}")
        
        # Set default description if missing
        if not self.api_description:
            self.api_description = f"Tool: {self.api_name}"
        
        return self
    
    def get_endpoint(self) -> str:
        """Get the endpoint URL, stripped of whitespace."""
        return (self.api_endpoint or "").strip()
    
    def get_parameters(self) -> List[ToolParameter]:
        """Parse and return parameters as ToolParameter objects."""
        params = []
        
        # Try to get params from requestJson first
        if self.request_json:
            try:
                req_data = json.loads(self.request_json)
                
                # Check for inputs array in requestJson
                if "inputs" in req_data and isinstance(req_data["inputs"], list):
                    for param_def in req_data["inputs"]:
                        try:
                            params.append(ToolParameter(**param_def))
                        except Exception as e:
                            # Log but continue with other params
                            print(f"Warning: Failed to parse parameter {param_def}: {e}")
                    return params
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse requestJson: {e}")
        
        # Fall back to apiParams
        if self.api_params:
            try:
                params_data = json.loads(self.api_params) if isinstance(self.api_params, str) else self.api_params
                
                if isinstance(params_data, list):
                    for param_def in params_data:
                        try:
                            params.append(ToolParameter(**param_def))
                        except Exception as e:
                            print(f"Warning: Failed to parse parameter {param_def}: {e}")
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse apiParams: {e}")
        
        return params


class APIToolListResponse(BaseModel):
    """Model for the API response containing tool definitions."""
    
    data: Dict[str, Any] = Field(..., description="Response data")
    
    def get_tool_list(self) -> List[ToolDefinition]:
        """Extract and validate tool definitions from response."""
        tools = []
        
        # Check if data is a list (some APIs return this)
        if isinstance(self.data, list):
            if not self.data:
                print("Warning: API returned empty list for 'data' field")
                return []
            
            print(f"Warning: 'data' field is a list, expected dict")
            return []
        
        # Expected structure: { "data": { "aiRestApiList": [...] } }
        if not isinstance(self.data, dict):
            print(f"Warning: 'data' field is not a dict: {type(self.data)}")
            return []
        
        tool_list = self.data.get("aiRestApiList", [])
        
        if not isinstance(tool_list, list):
            print(f"Warning: 'aiRestApiList' is not a list: {type(tool_list)}")
            return []
        
        for tool_def in tool_list:
            try:
                tool = ToolDefinition(**tool_def)
                tools.append(tool)
            except Exception as e:
                # Log the error but continue with other tools
                tool_name = tool_def.get("apiName", "unknown")
                print(f"Warning: Failed to parse tool '{tool_name}': {e}")
        
        return tools
