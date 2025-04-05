"""
Error handling module for HubQueue.
"""
import os
import sys
import traceback
import inspect
import json
from typing import Dict, Any, Optional, List, Tuple, Callable
from .logging import get_logger

# Get logger
logger = get_logger()

# Define error types
class HubQueueError(Exception):
    """Base exception class for HubQueue."""

    def __init__(self, message: str, code: int = 1, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a HubQueueError.

        Args:
            message (str): Error message
            code (int, optional): Error code. Defaults to 1.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary.

        Returns:
            Dict[str, Any]: Error dictionary
        """
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        """
        Convert error to string.

        Returns:
            str: Error string
        """
        if self.details:
            return f"{self.message} (Code: {self.code}, Details: {self.details})"
        return f"{self.message} (Code: {self.code})"


class AuthenticationError(HubQueueError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed", code: int = 401, details: Optional[Dict[str, Any]] = None):
        """
        Initialize an AuthenticationError.

        Args:
            message (str, optional): Error message. Defaults to "Authentication failed".
            code (int, optional): Error code. Defaults to 401.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class AuthorizationError(HubQueueError):
    """Authorization error."""

    def __init__(self, message: str = "Authorization failed", code: int = 403, details: Optional[Dict[str, Any]] = None):
        """
        Initialize an AuthorizationError.

        Args:
            message (str, optional): Error message. Defaults to "Authorization failed".
            code (int, optional): Error code. Defaults to 403.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class NotFoundError(HubQueueError):
    """Not found error."""

    def __init__(self, message: str = "Resource not found", code: int = 404, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a NotFoundError.

        Args:
            message (str, optional): Error message. Defaults to "Resource not found".
            code (int, optional): Error code. Defaults to 404.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class ValidationError(HubQueueError):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", code: int = 422, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a ValidationError.

        Args:
            message (str, optional): Error message. Defaults to "Validation failed".
            code (int, optional): Error code. Defaults to 422.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class RateLimitError(HubQueueError):
    """Rate limit error."""

    def __init__(self, message: str = "Rate limit exceeded", code: int = 429, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a RateLimitError.

        Args:
            message (str, optional): Error message. Defaults to "Rate limit exceeded".
            code (int, optional): Error code. Defaults to 429.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class ServerError(HubQueueError):
    """Server error."""

    def __init__(self, message: str = "Server error", code: int = 500, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a ServerError.

        Args:
            message (str, optional): Error message. Defaults to "Server error".
            code (int, optional): Error code. Defaults to 500.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class ConfigurationError(HubQueueError):
    """Configuration error."""

    def __init__(self, message: str = "Configuration error", code: int = 1001, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a ConfigurationError.

        Args:
            message (str, optional): Error message. Defaults to "Configuration error".
            code (int, optional): Error code. Defaults to 1001.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class NetworkError(HubQueueError):
    """Network error."""

    def __init__(self, message: str = "Network error", code: int = 1002, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a NetworkError.

        Args:
            message (str, optional): Error message. Defaults to "Network error".
            code (int, optional): Error code. Defaults to 1002.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


class InputError(HubQueueError):
    """Input error."""

    def __init__(self, message: str = "Invalid input", code: int = 1003, details: Optional[Dict[str, Any]] = None):
        """
        Initialize an InputError.

        Args:
            message (str, optional): Error message. Defaults to "Invalid input".
            code (int, optional): Error code. Defaults to 1003.
            details (Dict[str, Any], optional): Error details. Defaults to None.
        """
        super().__init__(message, code, details)


# Error handling functions
def handle_error(error: Exception, debug: bool = False) -> Dict[str, Any]:
    """
    Handle an error.

    Args:
        error (Exception): Error to handle
        debug (bool, optional): Whether to include debug information. Defaults to False.

    Returns:
        Dict[str, Any]: Error information
    """
    # Log error
    logger.error(f"Error: {str(error)}")

    # Get error information
    error_type = type(error).__name__
    error_message = str(error)
    error_traceback = traceback.format_exc()

    # Log traceback
    logger.debug(f"Traceback: {error_traceback}")

    # Create error information
    error_info = {
        "error": True,
        "type": error_type,
        "message": error_message,
    }

    # Add debug information if requested
    if debug:
        error_info["traceback"] = error_traceback
        error_info["frame"] = get_frame_info()

    # Convert HubQueueError to dictionary
    if isinstance(error, HubQueueError):
        error_info.update(error.to_dict())

    return error_info


def get_frame_info() -> Dict[str, Any]:
    """
    Get information about the current frame.

    Returns:
        Dict[str, Any]: Frame information
    """
    try:
        # Get current frame
        frame = inspect.currentframe()

        # Get caller frame
        caller_frame = frame.f_back.f_back if frame and frame.f_back else None

        # Get frame information
        if caller_frame:
            frame_info = {
                "file": caller_frame.f_code.co_filename,
                "line": caller_frame.f_lineno,
                "function": caller_frame.f_code.co_name,
                "locals": {k: str(v) for k, v in caller_frame.f_locals.items()},
            }
        else:
            frame_info = {}

        return frame_info
    except Exception:
        # Return empty dict if anything goes wrong
        return {}


def get_error_suggestion(error: Exception) -> Optional[str]:
    """
    Get a suggestion for resolving an error.

    Args:
        error (Exception): Error to get suggestion for

    Returns:
        Optional[str]: Suggestion or None if no suggestion is available
    """
    # Define error suggestions
    suggestions = {
        AuthenticationError: [
            "Check your GitHub token",
            "Try authenticating again",
            "Make sure your token has the required scopes",
        ],
        AuthorizationError: [
            "Check your permissions for the repository",
            "Make sure your token has the required scopes",
            "Contact the repository owner for access",
        ],
        NotFoundError: [
            "Check the resource name or ID",
            "Make sure the resource exists",
            "Check your spelling",
        ],
        ValidationError: [
            "Check your input values",
            "Make sure all required fields are provided",
            "Check the format of your input",
        ],
        RateLimitError: [
            "Wait and try again later",
            "Reduce the frequency of your requests",
            "Use conditional requests to reduce API usage",
        ],
        ServerError: [
            "Try again later",
            "Check the GitHub status page",
            "Contact GitHub support if the issue persists",
        ],
        ConfigurationError: [
            "Check your configuration file",
            "Make sure all required configuration values are set",
            "Try resetting your configuration",
        ],
        NetworkError: [
            "Check your internet connection",
            "Try again later",
            "Check if GitHub is down",
        ],
        InputError: [
            "Check your input values",
            "Make sure all required fields are provided",
            "Check the format of your input",
        ],
    }

    # Get suggestion for error type
    for error_type, error_suggestions in suggestions.items():
        if isinstance(error, error_type):
            # Return a random suggestion
            import random
            return random.choice(error_suggestions)

    # No suggestion available
    return None


def format_error_message(error: Exception, include_suggestion: bool = True, debug: bool = False) -> str:
    """
    Format an error message for display.

    Args:
        error (Exception): Error to format
        include_suggestion (bool, optional): Whether to include a suggestion. Defaults to True.
        debug (bool, optional): Whether to include debug information. Defaults to False.

    Returns:
        str: Formatted error message
    """
    # Get error message
    message = str(error)

    # Add error type if not a HubQueueError
    if not isinstance(error, HubQueueError):
        message = f"{type(error).__name__}: {message}"

    # Add suggestion if requested
    if include_suggestion:
        suggestion = get_error_suggestion(error)
        if suggestion:
            message = f"{message}\n\nSuggestion: {suggestion}"

    # Add debug information if requested
    if debug:
        traceback_str = traceback.format_exc()
        frame_info = get_frame_info()

        message = f"{message}\n\nTraceback:\n{traceback_str}\n\nFrame:\n{json.dumps(frame_info, indent=2)}"

    return message


def error_handler(func: Callable) -> Callable:
    """
    Decorator for handling errors.

    Args:
        func (Callable): Function to decorate

    Returns:
        Callable: Decorated function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Handle error
            error_info = handle_error(e)

            # Log error
            logger.error(f"Error in {func.__name__}: {str(e)}")

            # Return error information
            return error_info

    return wrapper


def validate_input(value: Any, validators: List[Callable[[Any], Tuple[bool, Optional[str]]]]) -> Tuple[bool, Optional[str]]:
    """
    Validate input value.

    Args:
        value (Any): Value to validate
        validators (List[Callable[[Any], Tuple[bool, Optional[str]]]]): Validators to use

    Returns:
        Tuple[bool, Optional[str]]: Validation result and error message
    """
    # Run validators
    for validator in validators:
        valid, error = validator(value)
        if not valid:
            return False, error

    return True, None


def is_debug_mode() -> bool:
    """
    Check if debug mode is enabled.

    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    # Check environment variable
    debug_env = os.environ.get("HUBQUEUE_DEBUG", "").lower()
    if debug_env in ("1", "true", "yes", "on"):
        return True

    # Check command line arguments
    if "--debug" in sys.argv:
        return True

    return False


# Initialize debug mode
DEBUG_MODE = is_debug_mode()


def set_debug_mode(enabled: bool = True) -> None:
    """
    Set debug mode.

    Args:
        enabled (bool, optional): Whether to enable debug mode. Defaults to True.
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled

    # Set logger level
    if enabled:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")


def get_debug_mode() -> bool:
    """
    Get debug mode.

    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    return DEBUG_MODE
