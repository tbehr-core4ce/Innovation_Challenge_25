from typing import Any, Optional

from fastapi import HTTPException, status

from .logging import get_logger

logger = get_logger(__name__)


class BETSError(HTTPException):
    """Base error class for BETS application with logging."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error: Optional[Exception] = None,
        **kwargs: Any
    ):
        """
        Initialize BETS error with automatic logging.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error: Original exception if this is wrapping another error
            **kwargs: Additional context to log
        """
        super().__init__(status_code=status_code, detail=message)
        
        # Log based on severity
        if status_code >= 500:
            logger.error(
                message,
                status_code=status_code,
                original_error=str(error) if error else None,
                **kwargs
            )
        elif status_code >= 400:
            logger.warning(
                message,
                status_code=status_code,
                original_error=str(error) if error else None,
                **kwargs
            )
        else:
            logger.debug(
                message,
                status_code=status_code,
                **kwargs
            )


class NotFoundError(BETSError):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(BETSError):
    """Invalid input or parameters error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            message = f"{field}: {message}"
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(BETSError):
    """Authentication required error."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(BETSError):
    """Insufficient permissions error."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(BETSError):
    """Resource conflict error."""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        if resource:
            message = f"{resource}: {message}"
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class ServerError(BETSError):
    """Internal server error."""
    
    def __init__(self, message: str = "Internal server error", error: Optional[Exception] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=error
        )


# Convenience functions for common error patterns
def failed(operation: str, error: Optional[Exception] = None, status_code: int = 500) -> None:
    """
    Raise an error for a failed operation.
    
    Args:
        operation: Description of what failed
        error: Original exception
        status_code: HTTP status code
        
    Raises:
        BETSError: Always raises
    """
    raise BETSError(f"Failed to {operation.lower()}", status_code, error)


def require_value(value: Any, name: str) -> None:
    """
    Ensure a required value is present.
    
    Args:
        value: Value to check
        name: Name of the value for error message
        
    Raises:
        ValidationError: If value is None or empty
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"Must provide {name.lower()}")


def not_found(resource: str, identifier: Any = None) -> None:
    """
    Raise a not found error.
    
    Args:
        resource: Type of resource
        identifier: Resource identifier
        
    Raises:
        NotFoundError: Always raises
    """
    raise NotFoundError(resource, identifier)


def unauthorized(message: str = "Not authorized") -> None:
    """
    Raise an unauthorized error.
    
    Args:
        message: Error message
        
    Raises:
        UnauthorizedError: Always raises
    """
    raise UnauthorizedError(message)


def forbidden(message: str = "Forbidden") -> None:
    """
    Raise a forbidden error.
    
    Args:
        message: Error message
        
    Raises:
        ForbiddenError: Always raises
    """
    raise ForbiddenError(message)