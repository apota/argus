"""
Custom exceptions for the Argus AWS Explorer library.
"""


class ArgusException(Exception):
    """Base exception class for Argus library."""
    pass


class AWSResourceException(ArgusException):
    """Exception raised when AWS resource operations fail."""
    
    def __init__(self, resource_type: str, operation: str, message: str):
        self.resource_type = resource_type
        self.operation = operation
        self.message = message
        super().__init__(f"AWS {resource_type} {operation} failed: {message}")


class AWSConnectionException(ArgusException):
    """Exception raised when AWS connection fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"AWS connection failed: {message}")


class AWSPermissionException(ArgusException):
    """Exception raised when AWS operation is denied due to permissions."""
    
    def __init__(self, resource_type: str, operation: str, message: str = ""):
        self.resource_type = resource_type
        self.operation = operation
        self.message = message
        super().__init__(f"Permission denied for {resource_type} {operation}: {message}")
