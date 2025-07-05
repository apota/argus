"""
Custom exceptions for the Argus AWS Explorer library.
"""


class ArgusException(Exception):
    """Base exception class for Argus library."""
    pass


class AWSResourceError(ArgusException):
    """Exception raised when AWS resource operations fail."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AWSResourceError):
    """Exception raised when an AWS resource is not found."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AWSConnectionError(ArgusException):
    """Exception raised when AWS connection fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"AWS connection failed: {message}")


class AWSPermissionError(ArgusException):
    """Exception raised when AWS operation is denied due to permissions."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Permission denied: {message}")


# Legacy aliases for backward compatibility
AWSResourceException = AWSResourceError
AWSConnectionException = AWSConnectionError
AWSPermissionException = AWSPermissionError
