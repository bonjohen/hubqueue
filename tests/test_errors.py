"""
Tests for the errors module.
"""
import os
import sys
import json
import tempfile
from unittest import TestCase, mock

from hubqueue.errors import (
    HubQueueError, AuthenticationError, AuthorizationError, NotFoundError,
    ValidationError, RateLimitError, ServerError, ConfigurationError,
    NetworkError, InputError, handle_error, get_frame_info,
    get_error_suggestion, format_error_message, error_handler,
    validate_input, is_debug_mode, set_debug_mode, get_debug_mode
)


class TestErrors(TestCase):
    """Test error handling functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

        # Save original debug mode
        self.original_debug_mode = get_debug_mode()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()

        # Restore original debug mode
        set_debug_mode(self.original_debug_mode)

        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_hubqueue_error(self):
        """Test HubQueueError."""
        # Create error
        error = HubQueueError("Test error", 123, {"key": "value"})

        # Verify error
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, 123)
        self.assertEqual(error.details, {"key": "value"})
        self.assertEqual(str(error), "Test error (Code: 123, Details: {'key': 'value'})")

        # Verify to_dict
        self.assertEqual(error.to_dict(), {
            "error": True,
            "code": 123,
            "message": "Test error",
            "details": {"key": "value"},
        })

        # Test without details
        error = HubQueueError("Test error", 123)
        self.assertEqual(str(error), "Test error (Code: 123)")

    def test_authentication_error(self):
        """Test AuthenticationError."""
        # Create error
        error = AuthenticationError()

        # Verify error
        self.assertEqual(error.message, "Authentication failed")
        self.assertEqual(error.code, 401)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = AuthenticationError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_authorization_error(self):
        """Test AuthorizationError."""
        # Create error
        error = AuthorizationError()

        # Verify error
        self.assertEqual(error.message, "Authorization failed")
        self.assertEqual(error.code, 403)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = AuthorizationError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_not_found_error(self):
        """Test NotFoundError."""
        # Create error
        error = NotFoundError()

        # Verify error
        self.assertEqual(error.message, "Resource not found")
        self.assertEqual(error.code, 404)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = NotFoundError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_validation_error(self):
        """Test ValidationError."""
        # Create error
        error = ValidationError()

        # Verify error
        self.assertEqual(error.message, "Validation failed")
        self.assertEqual(error.code, 422)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = ValidationError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        # Create error
        error = RateLimitError()

        # Verify error
        self.assertEqual(error.message, "Rate limit exceeded")
        self.assertEqual(error.code, 429)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = RateLimitError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_server_error(self):
        """Test ServerError."""
        # Create error
        error = ServerError()

        # Verify error
        self.assertEqual(error.message, "Server error")
        self.assertEqual(error.code, 500)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = ServerError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_configuration_error(self):
        """Test ConfigurationError."""
        # Create error
        error = ConfigurationError()

        # Verify error
        self.assertEqual(error.message, "Configuration error")
        self.assertEqual(error.code, 1001)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = ConfigurationError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_network_error(self):
        """Test NetworkError."""
        # Create error
        error = NetworkError()

        # Verify error
        self.assertEqual(error.message, "Network error")
        self.assertEqual(error.code, 1002)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = NetworkError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_input_error(self):
        """Test InputError."""
        # Create error
        error = InputError()

        # Verify error
        self.assertEqual(error.message, "Invalid input")
        self.assertEqual(error.code, 1003)
        self.assertEqual(error.details, {})

        # Create error with custom message
        error = InputError("Custom message")
        self.assertEqual(error.message, "Custom message")

    def test_handle_error(self):
        """Test handle_error function."""
        # Test with HubQueueError
        error = HubQueueError("Test error", 123, {"key": "value"})
        error_info = handle_error(error)

        self.assertEqual(error_info["error"], True)
        self.assertEqual(error_info["type"], "HubQueueError")
        self.assertEqual(error_info["message"], "Test error")
        self.assertEqual(error_info["code"], 123)
        self.assertEqual(error_info["details"], {"key": "value"})

        # Test with standard exception
        error = ValueError("Test error")
        error_info = handle_error(error)

        self.assertEqual(error_info["error"], True)
        self.assertEqual(error_info["type"], "ValueError")
        self.assertEqual(error_info["message"], "Test error")

        # Test with debug mode
        error = ValueError("Test error")
        error_info = handle_error(error, debug=True)

        self.assertEqual(error_info["error"], True)
        self.assertEqual(error_info["type"], "ValueError")
        self.assertEqual(error_info["message"], "Test error")
        self.assertIn("traceback", error_info)
        self.assertIn("frame", error_info)

    def test_get_frame_info(self):
        """Test get_frame_info function."""
        # Mock inspect.currentframe to return a frame with known values
        with mock.patch('inspect.currentframe') as mock_currentframe:
            # Create mock frames
            mock_frame = mock.MagicMock()
            mock_caller_frame = mock.MagicMock()

            # Set up frame chain
            mock_frame.f_back = mock.MagicMock()
            mock_frame.f_back.f_back = mock_caller_frame

            # Set up caller frame attributes
            mock_caller_frame.f_code.co_filename = 'test_errors.py'
            mock_caller_frame.f_lineno = 123
            mock_caller_frame.f_code.co_name = 'test_function'
            mock_caller_frame.f_locals = {'arg1': 'value1', 'arg2': 'value2'}

            # Set up mock return value
            mock_currentframe.return_value = mock_frame

            # Get frame info
            frame_info = get_frame_info()

            # Verify frame info
            self.assertIn("file", frame_info)
            self.assertIn("line", frame_info)
            self.assertIn("function", frame_info)
            self.assertIn("locals", frame_info)

            # Verify values
            self.assertEqual(frame_info["file"], "test_errors.py")
            self.assertEqual(frame_info["line"], 123)
            self.assertEqual(frame_info["function"], "test_function")
            self.assertEqual(len(frame_info["locals"]), 2)

    def test_get_error_suggestion(self):
        """Test get_error_suggestion function."""
        # Test with HubQueueError
        error = HubQueueError("Test error")
        suggestion = get_error_suggestion(error)

        # No suggestion for HubQueueError
        self.assertIsNone(suggestion)

        # Test with AuthenticationError
        error = AuthenticationError()
        suggestion = get_error_suggestion(error)

        # Suggestion for AuthenticationError
        self.assertIsNotNone(suggestion)

        # Test with standard exception
        error = ValueError("Test error")
        suggestion = get_error_suggestion(error)

        # No suggestion for standard exception
        self.assertIsNone(suggestion)

    def test_format_error_message(self):
        """Test format_error_message function."""
        # Test with HubQueueError
        error = HubQueueError("Test error", 123)
        message = format_error_message(error)

        # Verify message
        self.assertEqual(message, "Test error (Code: 123)")

        # Test with standard exception
        error = ValueError("Test error")
        message = format_error_message(error)

        # Verify message
        self.assertEqual(message, "ValueError: Test error")

        # Test with suggestion
        error = AuthenticationError()
        message = format_error_message(error, include_suggestion=True)

        # Verify message
        self.assertIn("Authentication failed", message)
        self.assertIn("Suggestion:", message)

        # Test without suggestion
        error = AuthenticationError()
        message = format_error_message(error, include_suggestion=False)

        # Verify message
        self.assertEqual(message, "Authentication failed (Code: 401)")

        # Test with debug mode
        error = ValueError("Test error")
        message = format_error_message(error, debug=True)

        # Verify message
        self.assertIn("ValueError: Test error", message)
        self.assertIn("Traceback:", message)
        self.assertIn("Frame:", message)

    def test_error_handler(self):
        """Test error_handler decorator."""
        # Define test function
        @error_handler
        def test_function(arg):
            if arg == "error":
                raise ValueError("Test error")
            return arg

        # Test without error
        result = test_function("test")
        self.assertEqual(result, "test")

        # Test with error
        result = test_function("error")
        self.assertEqual(result["error"], True)
        self.assertEqual(result["type"], "ValueError")
        self.assertEqual(result["message"], "Test error")

    def test_validate_input(self):
        """Test validate_input function."""
        # Define validators
        validators = [
            lambda x: (x is not None, "Value is required"),
            lambda x: (isinstance(x, str), "Value must be a string"),
            lambda x: (len(x) >= 3, "Value must be at least 3 characters"),
        ]

        # Test valid input
        valid, error = validate_input("test", validators)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # Test invalid input (None)
        valid, error = validate_input(None, validators)
        self.assertFalse(valid)
        self.assertEqual(error, "Value is required")

        # Test invalid input (not a string)
        valid, error = validate_input(123, validators)
        self.assertFalse(valid)
        self.assertEqual(error, "Value must be a string")

        # Test invalid input (too short)
        valid, error = validate_input("ab", validators)
        self.assertFalse(valid)
        self.assertEqual(error, "Value must be at least 3 characters")

    def test_is_debug_mode(self):
        """Test is_debug_mode function."""
        # Test with environment variable
        with mock.patch.dict('os.environ', {"HUBQUEUE_DEBUG": "1"}):
            self.assertTrue(is_debug_mode())

        with mock.patch.dict('os.environ', {"HUBQUEUE_DEBUG": "true"}):
            self.assertTrue(is_debug_mode())

        with mock.patch.dict('os.environ', {"HUBQUEUE_DEBUG": "yes"}):
            self.assertTrue(is_debug_mode())

        with mock.patch.dict('os.environ', {"HUBQUEUE_DEBUG": "on"}):
            self.assertTrue(is_debug_mode())

        with mock.patch.dict('os.environ', {"HUBQUEUE_DEBUG": "0"}):
            self.assertFalse(is_debug_mode())

        # Test with command line arguments
        with mock.patch('sys.argv', ["hubqueue", "--debug"]):
            self.assertTrue(is_debug_mode())

        with mock.patch('sys.argv', ["hubqueue"]):
            self.assertFalse(is_debug_mode())

    def test_set_debug_mode(self):
        """Test set_debug_mode function."""
        # Test enabling debug mode
        set_debug_mode(True)
        self.assertTrue(get_debug_mode())

        # Test disabling debug mode
        set_debug_mode(False)
        self.assertFalse(get_debug_mode())
