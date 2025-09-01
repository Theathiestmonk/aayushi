"""
MCP Custom Exceptions for proper error handling
"""

from typing import Optional, Dict, Any

class MCPError(Exception):
    """Base exception for MCP-related errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or "MCP_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.error_code}: {self.message}"

class ToolNotFoundError(MCPError):
    """Raised when a requested tool is not found"""
    
    def __init__(self, tool_name: str):
        super().__init__(
            message=f"Tool '{tool_name}' not found",
            error_code="TOOL_NOT_FOUND",
            details={"tool_name": tool_name}
        )

class InvalidParametersError(MCPError):
    """Raised when tool parameters are invalid"""
    
    def __init__(self, tool_name: str, missing_params: list, invalid_params: Optional[Dict[str, str]] = None):
        super().__init__(
            message=f"Invalid parameters for tool '{tool_name}'",
            error_code="INVALID_PARAMETERS",
            details={
                "tool_name": tool_name,
                "missing_params": missing_params,
                "invalid_params": invalid_params or {}
            }
        )

class ToolExecutionError(MCPError):
    """Raised when tool execution fails"""
    
    def __init__(self, tool_name: str, original_error: Exception, execution_context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Tool '{tool_name}' execution failed: {str(original_error)}",
            error_code="TOOL_EXECUTION_ERROR",
            details={
                "tool_name": tool_name,
                "original_error": str(original_error),
                "error_type": type(original_error).__name__,
                "execution_context": execution_context or {}
            }
        )

class ToolTimeoutError(MCPError):
    """Raised when tool execution times out"""
    
    def __init__(self, tool_name: str, timeout_seconds: float):
        super().__init__(
            message=f"Tool '{tool_name}' execution timed out after {timeout_seconds} seconds",
            error_code="TOOL_TIMEOUT",
            details={
                "tool_name": tool_name,
                "timeout_seconds": timeout_seconds
            }
        )

class ToolRateLimitError(MCPError):
    """Raised when tool rate limit is exceeded"""
    
    def __init__(self, tool_name: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Tool '{tool_name}' rate limit exceeded",
            error_code="TOOL_RATE_LIMIT",
            details={
                "tool_name": tool_name,
                "retry_after": retry_after
            }
        )

class SessionError(MCPError):
    """Raised when there's a session-related error"""
    
    def __init__(self, session_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Session error: {message}",
            error_code="SESSION_ERROR",
            details={
                "session_id": session_id,
                **details or {}
            }
        )

class AuthenticationError(MCPError):
    """Raised when authentication fails"""
    
    def __init__(self, user_id: str, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details={"user_id": user_id}
        )

class AuthorizationError(MCPError):
    """Raised when user is not authorized to use a tool"""
    
    def __init__(self, user_id: str, tool_name: str, required_permissions: Optional[list] = None):
        super().__init__(
            message=f"User '{user_id}' not authorized to use tool '{tool_name}'",
            error_code="AUTHORIZATION_ERROR",
            details={
                "user_id": user_id,
                "tool_name": tool_name,
                "required_permissions": required_permissions or []
            }
        )

class ConfigurationError(MCPError):
    """Raised when MCP configuration is invalid"""
    
    def __init__(self, config_key: str, message: str):
        super().__init__(
            message=f"Configuration error: {message}",
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key}
        )

class ExternalServiceError(MCPError):
    """Raised when external service integration fails"""
    
    def __init__(self, service_name: str, operation: str, original_error: Exception):
        super().__init__(
            message=f"External service '{service_name}' operation '{operation}' failed: {str(original_error)}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={
                "service_name": service_name,
                "operation": operation,
                "original_error": str(original_error),
                "error_type": type(original_error).__name__
            }
        )




