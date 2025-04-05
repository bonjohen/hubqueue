"""
Error handling CLI module for HubQueue.
"""
import os
import sys
import traceback
import json
from typing import Dict, Any, Optional, List, Tuple, Callable
import click
from .errors import (
    HubQueueError, AuthenticationError, AuthorizationError, NotFoundError,
    ValidationError, RateLimitError, ServerError, ConfigurationError,
    NetworkError, InputError, handle_error, get_error_suggestion,
    format_error_message, is_debug_mode, set_debug_mode, get_debug_mode
)
from .ui import (
    Color, print_color, print_error, print_warning, print_info,
    print_debug, confirm, is_color_enabled
)
from .logging import get_logger

# Get logger
logger = get_logger()


def print_error_message(error: Exception, include_suggestion: bool = True, debug: bool = False) -> None:
    """
    Print an error message to the console.

    Args:
        error (Exception): Error to print
        include_suggestion (bool, optional): Whether to include a suggestion. Defaults to True.
        debug (bool, optional): Whether to include debug information. Defaults to False.
    """
    # Get error message
    message = str(error)

    # Add error type if not a HubQueueError
    if not isinstance(error, HubQueueError):
        message = f"{type(error).__name__}: {message}"

    # Print error message
    print_error(message)

    # Print suggestion if requested
    if include_suggestion:
        suggestion = get_error_suggestion(error)
        if suggestion:
            print_info(f"Suggestion: {suggestion}")

    # Print debug information if requested
    if debug or get_debug_mode():
        print_debug("Debug Information:")
        traceback_str = traceback.format_exc()
        print_color(traceback_str, Color.MAGENTA, dim=True)

        # Get frame info safely
        frame_info = {}
        try:
            tb = sys.exc_info()[2]
            if tb:
                frames = traceback.extract_tb(tb)
                if frames:
                    frame = frames[-1]
                    frame_info = {
                        "file": frame.filename,
                        "line": frame.lineno,
                        "function": frame.name,
                    }
        except Exception:
            pass

        print_color(json.dumps(frame_info, indent=2), Color.MAGENTA, dim=True)


def handle_cli_error(error: Exception, exit_on_error: bool = True, include_suggestion: bool = True) -> None:
    """
    Handle an error in the CLI.

    Args:
        error (Exception): Error to handle
        exit_on_error (bool, optional): Whether to exit on error. Defaults to True.
        include_suggestion (bool, optional): Whether to include a suggestion. Defaults to True.
    """
    # Log error
    logger.error(f"Error: {str(error)}")

    # Print error message
    print_error_message(error, include_suggestion, get_debug_mode())

    # Exit if requested
    if exit_on_error:
        sys.exit(1)


def cli_error_handler(exit_on_error: bool = True, include_suggestion: bool = True) -> Callable:
    """
    Decorator for handling errors in CLI commands.

    Args:
        exit_on_error (bool, optional): Whether to exit on error. Defaults to True.
        include_suggestion (bool, optional): Whether to include a suggestion. Defaults to True.

    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Handle error
                handle_cli_error(e, exit_on_error, include_suggestion)

        return wrapper

    return decorator


def validate_cli_input(value: Any, validators: List[Callable[[Any], Tuple[bool, Optional[str]]]]) -> Any:
    """
    Validate CLI input value.

    Args:
        value (Any): Value to validate
        validators (List[Callable[[Any], Tuple[bool, Optional[str]]]]): Validators to use

    Returns:
        Any: Validated value

    Raises:
        InputError: If validation fails
    """
    # Run validators
    for validator in validators:
        valid, error = validator(value)
        if not valid:
            raise InputError(error or "Invalid input")

    return value


def prompt_for_retry(error: Exception) -> bool:
    """
    Prompt the user to retry after an error.

    Args:
        error (Exception): Error that occurred

    Returns:
        bool: True if the user wants to retry, False otherwise
    """
    # Print error message
    print_error_message(error, include_suggestion=True, debug=False)

    # Prompt for retry
    return confirm("Do you want to retry?", default=True)


def show_error_details(error: Exception) -> None:
    """
    Show detailed information about an error.

    Args:
        error (Exception): Error to show details for
    """
    # Get error information
    error_info = handle_error(error, debug=True)

    # Print error information
    print_error("Error Details:")
    print_color(json.dumps(error_info, indent=2), Color.RED, dim=True)


def create_error_report(error: Exception, include_system_info: bool = True) -> Dict[str, Any]:
    """
    Create an error report.

    Args:
        error (Exception): Error to create report for
        include_system_info (bool, optional): Whether to include system information. Defaults to True.

    Returns:
        Dict[str, Any]: Error report
    """
    # Get error information
    error_info = handle_error(error, debug=True)

    # Create error report
    report = {
        "error": error_info,
        "timestamp": get_timestamp(),
    }

    # Add system information if requested
    if include_system_info:
        import platform

        report["system"] = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    return report


def save_error_report(report: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """
    Save an error report to a file.

    Args:
        report (Dict[str, Any]): Error report to save
        file_path (Optional[str], optional): File path to save to. Defaults to None.

    Returns:
        str: File path
    """
    # Generate file path if not provided
    if not file_path:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"hubqueue_error_{timestamp}.json"

    # Save report to file
    with open(file_path, "w") as f:
        json.dump(report, f, indent=2)

    return file_path


def get_timestamp():
    """
    Get current timestamp.

    Returns:
        str: Current timestamp in ISO format
    """
    import datetime
    return datetime.datetime.now().isoformat()
