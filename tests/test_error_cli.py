"""
Tests for the error_cli module.
"""
import os
import sys
import json
import tempfile
from unittest import TestCase, mock

from hubqueue.errors import (
    HubQueueError, AuthenticationError, AuthorizationError, NotFoundError,
    ValidationError, RateLimitError, ServerError, ConfigurationError,
    NetworkError, InputError, set_debug_mode, get_debug_mode
)
from hubqueue.error_cli import (
    print_error_message, handle_cli_error, cli_error_handler,
    validate_cli_input, prompt_for_retry, show_error_details,
    create_error_report, save_error_report
)


class TestErrorCLI(TestCase):
    """Test error CLI functions."""

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

    @mock.patch('hubqueue.error_cli.print_error')
    @mock.patch('hubqueue.error_cli.print_info')
    @mock.patch('hubqueue.error_cli.print_debug')
    @mock.patch('hubqueue.error_cli.print_color')
    def test_print_error_message(self, mock_print_color, mock_print_debug, mock_print_info, mock_print_error):
        """Test print_error_message function."""
        # Test with HubQueueError
        error = HubQueueError("Test error", 123)
        print_error_message(error)
        
        # Verify print_error called
        mock_print_error.assert_called_once_with("Test error (Code: 123)")
        
        # Reset mocks
        mock_print_error.reset_mock()
        mock_print_info.reset_mock()
        mock_print_debug.reset_mock()
        mock_print_color.reset_mock()
        
        # Test with standard exception
        error = ValueError("Test error")
        print_error_message(error)
        
        # Verify print_error called
        mock_print_error.assert_called_once_with("ValueError: Test error")
        
        # Reset mocks
        mock_print_error.reset_mock()
        mock_print_info.reset_mock()
        mock_print_debug.reset_mock()
        mock_print_color.reset_mock()
        
        # Test with suggestion
        error = AuthenticationError()
        print_error_message(error, include_suggestion=True)
        
        # Verify print_error and print_info called
        mock_print_error.assert_called_once_with("Authentication failed (Code: 401)")
        mock_print_info.assert_called_once()
        
        # Reset mocks
        mock_print_error.reset_mock()
        mock_print_info.reset_mock()
        mock_print_debug.reset_mock()
        mock_print_color.reset_mock()
        
        # Test with debug mode
        error = ValueError("Test error")
        print_error_message(error, debug=True)
        
        # Verify print_error, print_debug, and print_color called
        mock_print_error.assert_called_once_with("ValueError: Test error")
        mock_print_debug.assert_called_once_with("Debug Information:")
        self.assertTrue(mock_print_color.called)

    @mock.patch('hubqueue.error_cli.print_error_message')
    @mock.patch('sys.exit')
    def test_handle_cli_error(self, mock_exit, mock_print_error_message):
        """Test handle_cli_error function."""
        # Test with exit_on_error=True
        error = ValueError("Test error")
        handle_cli_error(error)
        
        # Verify print_error_message and sys.exit called
        mock_print_error_message.assert_called_once()
        mock_exit.assert_called_once_with(1)
        
        # Reset mocks
        mock_print_error_message.reset_mock()
        mock_exit.reset_mock()
        
        # Test with exit_on_error=False
        error = ValueError("Test error")
        handle_cli_error(error, exit_on_error=False)
        
        # Verify print_error_message called but not sys.exit
        mock_print_error_message.assert_called_once()
        mock_exit.assert_not_called()

    def test_cli_error_handler(self):
        """Test cli_error_handler decorator."""
        # Define test function
        @cli_error_handler(exit_on_error=False)
        def test_function(arg):
            if arg == "error":
                raise ValueError("Test error")
            return arg
        
        # Mock handle_cli_error
        with mock.patch('hubqueue.error_cli.handle_cli_error') as mock_handle_cli_error:
            # Test without error
            result = test_function("test")
            self.assertEqual(result, "test")
            mock_handle_cli_error.assert_not_called()
            
            # Test with error
            result = test_function("error")
            self.assertIsNone(result)
            mock_handle_cli_error.assert_called_once()

    def test_validate_cli_input(self):
        """Test validate_cli_input function."""
        # Define validators
        validators = [
            lambda x: (x is not None, "Value is required"),
            lambda x: (isinstance(x, str), "Value must be a string"),
            lambda x: (len(x) >= 3, "Value must be at least 3 characters"),
        ]
        
        # Test valid input
        result = validate_cli_input("test", validators)
        self.assertEqual(result, "test")
        
        # Test invalid input
        with self.assertRaises(InputError):
            validate_cli_input(None, validators)
        
        with self.assertRaises(InputError):
            validate_cli_input(123, validators)
        
        with self.assertRaises(InputError):
            validate_cli_input("ab", validators)

    @mock.patch('hubqueue.error_cli.print_error_message')
    @mock.patch('hubqueue.error_cli.confirm')
    def test_prompt_for_retry(self, mock_confirm, mock_print_error_message):
        """Test prompt_for_retry function."""
        # Test with retry=True
        mock_confirm.return_value = True
        error = ValueError("Test error")
        result = prompt_for_retry(error)
        
        # Verify print_error_message and confirm called
        mock_print_error_message.assert_called_once()
        mock_confirm.assert_called_once_with("Do you want to retry?", default=True)
        self.assertTrue(result)
        
        # Reset mocks
        mock_print_error_message.reset_mock()
        mock_confirm.reset_mock()
        
        # Test with retry=False
        mock_confirm.return_value = False
        error = ValueError("Test error")
        result = prompt_for_retry(error)
        
        # Verify print_error_message and confirm called
        mock_print_error_message.assert_called_once()
        mock_confirm.assert_called_once_with("Do you want to retry?", default=True)
        self.assertFalse(result)

    @mock.patch('hubqueue.error_cli.print_error')
    @mock.patch('hubqueue.error_cli.print_color')
    def test_show_error_details(self, mock_print_color, mock_print_error):
        """Test show_error_details function."""
        # Test with error
        error = ValueError("Test error")
        show_error_details(error)
        
        # Verify print_error and print_color called
        mock_print_error.assert_called_once_with("Error Details:")
        mock_print_color.assert_called_once()

    def test_create_error_report(self):
        """Test create_error_report function."""
        # Test with error
        error = ValueError("Test error")
        report = create_error_report(error)
        
        # Verify report
        self.assertIn("error", report)
        self.assertIn("timestamp", report)
        self.assertEqual(report["error"]["type"], "ValueError")
        self.assertEqual(report["error"]["message"], "Test error")
        
        # Test with include_system_info=True
        error = ValueError("Test error")
        report = create_error_report(error, include_system_info=True)
        
        # Verify report
        self.assertIn("error", report)
        self.assertIn("timestamp", report)
        self.assertIn("system", report)
        self.assertIn("platform", report["system"])
        self.assertIn("python_version", report["system"])
        
        # Test with include_system_info=False
        error = ValueError("Test error")
        report = create_error_report(error, include_system_info=False)
        
        # Verify report
        self.assertIn("error", report)
        self.assertIn("timestamp", report)
        self.assertNotIn("system", report)

    def test_save_error_report(self):
        """Test save_error_report function."""
        # Create report
        report = {"error": {"message": "Test error"}}
        
        # Test with file_path
        file_path = os.path.join(self.temp_dir, "error_report.json")
        result = save_error_report(report, file_path)
        
        # Verify result
        self.assertEqual(result, file_path)
        self.assertTrue(os.path.exists(file_path))
        
        # Verify file content
        with open(file_path, "r") as f:
            content = json.load(f)
            self.assertEqual(content, report)
        
        # Test without file_path
        result = save_error_report(report)
        
        # Verify result
        self.assertTrue(os.path.exists(result))
        
        # Verify file content
        with open(result, "r") as f:
            content = json.load(f)
            self.assertEqual(content, report)
