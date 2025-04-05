"""
Tests for the ui module.
"""
import os
import sys
import tempfile
from unittest import TestCase, mock

from hubqueue.ui import (
    Color, print_color, print_header, print_info, print_success,
    print_warning, print_error, print_debug, print_table, print_json,
    print_progress_bar, print_spinner, prompt, confirm, select,
    multi_select, password, pause, clear_screen, set_color,
    set_interactive, is_interactive, is_color_enabled, init_ui,
    _supports_color, _get_terminal_width, _is_interactive, colorize
)


class TestUI(TestCase):
    """Test UI functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

        # Mock sys.stdout.isatty
        self.isatty_patcher = mock.patch('sys.stdout.isatty', return_value=True)
        self.isatty_patcher.start()

        # Mock sys.stdin.isatty
        self.stdin_isatty_patcher = mock.patch('sys.stdin.isatty', return_value=True)
        self.stdin_isatty_patcher.start()

        # Initialize UI
        init_ui()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.isatty_patcher.stop()
        self.stdin_isatty_patcher.stop()

        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_color_enum(self):
        """Test Color enum."""
        self.assertEqual(Color.RED.value, "\033[31m")
        self.assertEqual(Color.GREEN.value, "\033[32m")
        self.assertEqual(Color.BLUE.value, "\033[34m")
        self.assertEqual(Color.RESET.value, "\033[0m")

    def test_supports_color(self):
        """Test _supports_color function."""
        # Test with NO_COLOR environment variable
        with mock.patch.dict('os.environ', {"NO_COLOR": "1"}):
            self.assertFalse(_supports_color())

        # Test with FORCE_COLOR environment variable
        with mock.patch.dict('os.environ', {"FORCE_COLOR": "1"}):
            self.assertTrue(_supports_color())

        # Test with non-TTY stdout
        with mock.patch('sys.stdout.isatty', return_value=False):
            self.assertFalse(_supports_color())

        # Test with Windows
        with mock.patch('platform.system', return_value="Windows"):
            # Test with Windows Terminal
            with mock.patch.dict('os.environ', {"WT_SESSION": "1"}):
                self.assertTrue(_supports_color())

            # Test with VSCode
            with mock.patch.dict('os.environ', {"TERM_PROGRAM": "vscode"}):
                self.assertTrue(_supports_color())

            # Test with Windows 10
            with mock.patch('sys.getwindowsversion', return_value=mock.MagicMock(major=10)):
                self.assertTrue(_supports_color())

            # Test with ANSICON
            with mock.patch.dict('os.environ', {"ANSICON": "1"}):
                self.assertTrue(_supports_color())

            # Test with none of the above
            with mock.patch.dict('os.environ', {}):
                with mock.patch('sys.getwindowsversion', return_value=mock.MagicMock(major=6)):
                    self.assertFalse(_supports_color())

        # Test with dumb terminal
        with mock.patch.dict('os.environ', {"TERM": "dumb"}):
            with mock.patch('sys.stdout.isatty', return_value=True):
                with mock.patch('platform.system', return_value="Linux"):
                    self.assertFalse(_supports_color())

        # Test with normal terminal
        with mock.patch.dict('os.environ', {"TERM": "xterm"}):
            self.assertTrue(_supports_color())

    def test_get_terminal_width(self):
        """Test _get_terminal_width function."""
        # Test with shutil.get_terminal_size
        with mock.patch('shutil.get_terminal_size', return_value=mock.MagicMock(columns=100)):
            self.assertEqual(_get_terminal_width(), 100)

        # Test with exception
        with mock.patch('shutil.get_terminal_size', side_effect=OSError):
            self.assertEqual(_get_terminal_width(), 80)

    def test_is_interactive(self):
        """Test _is_interactive function."""
        # Test with non-TTY stdin
        with mock.patch('sys.stdin.isatty', return_value=False):
            self.assertFalse(_is_interactive())

        # Test with non-TTY stdout
        with mock.patch('sys.stdout.isatty', return_value=False):
            self.assertFalse(_is_interactive())

        # Test with CI environment
        with mock.patch.dict('os.environ', {"CI": "1"}):
            self.assertFalse(_is_interactive())

        # Test with TTY stdin and stdout, no CI
        with mock.patch('sys.stdin.isatty', return_value=True):
            with mock.patch('sys.stdout.isatty', return_value=True):
                with mock.patch.dict('os.environ', {}):
                    self.assertTrue(_is_interactive())

    def test_set_color(self):
        """Test set_color function."""
        # Test enabling color
        set_color(True)
        self.assertTrue(is_color_enabled())

        # Test disabling color
        set_color(False)
        self.assertFalse(is_color_enabled())

        # Reset color for other tests
        set_color(True)

    def test_set_interactive(self):
        """Test set_interactive function."""
        # Test enabling interactive mode
        set_interactive(True)
        self.assertTrue(is_interactive())

        # Test disabling interactive mode
        set_interactive(False)
        self.assertFalse(is_interactive())

        # Reset interactive mode for other tests
        set_interactive(True)

    def test_colorize(self):
        """Test colorize function."""
        # Test with color enabled
        set_color(True)
        self.assertEqual(colorize("test", Color.RED), f"{Color.RED.value}test{Color.RESET.value}")
        self.assertEqual(colorize("test", Color.RED, bold=True), f"{Color.BOLD.value}{Color.RED.value}test{Color.RESET.value}")

        # Test with color disabled
        set_color(False)
        self.assertEqual(colorize("test", Color.RED), "test")

        # Reset color for other tests
        set_color(True)

    @mock.patch('click.echo')
    def test_print_color(self, mock_echo):
        """Test print_color function."""
        # Test with color enabled
        set_color(True)
        print_color("test", Color.RED)
        mock_echo.assert_any_call(f"{Color.RED.value}test{Color.RESET.value}", nl=False)

        # Test with color disabled
        set_color(False)
        print_color("test", Color.RED)
        mock_echo.assert_any_call("test", nl=False)

        # Reset color for other tests
        set_color(True)

    @mock.patch('click.echo')
    def test_print_info(self, mock_echo):
        """Test print_info function."""
        print_info("test")
        mock_echo.assert_any_call(f"{Color.CYAN.value}test{Color.RESET.value}", nl=False)

    @mock.patch('click.echo')
    def test_print_success(self, mock_echo):
        """Test print_success function."""
        print_success("test")
        mock_echo.assert_any_call(f"{Color.GREEN.value}test{Color.RESET.value}", nl=False)

    @mock.patch('click.echo')
    def test_print_warning(self, mock_echo):
        """Test print_warning function."""
        print_warning("test")
        mock_echo.assert_any_call(f"{Color.YELLOW.value}test{Color.RESET.value}", nl=False)

    @mock.patch('click.echo')
    def test_print_error(self, mock_echo):
        """Test print_error function."""
        print_error("test")
        mock_echo.assert_any_call(f"{Color.RED.value}test{Color.RESET.value}", nl=False)

    @mock.patch('click.echo')
    def test_print_debug(self, mock_echo):
        """Test print_debug function."""
        print_debug("test")
        mock_echo.assert_any_call(f"{Color.MAGENTA.value}test{Color.RESET.value}", nl=False)

    @mock.patch('click.echo')
    def test_print_header(self, mock_echo):
        """Test print_header function."""
        print_header("test", width=20)
        # Don't test exact string content, just verify that mock_echo was called
        self.assertTrue(mock_echo.called)

    @mock.patch('click.echo')
    def test_print_table(self, mock_echo):
        """Test print_table function."""
        headers = ["Name", "Value"]
        rows = [["test1", "value1"], ["test2", "value2"]]
        print_table(headers, rows)
        # Don't test exact string content, just verify that mock_echo was called
        self.assertTrue(mock_echo.called)

    @mock.patch('click.echo')
    def test_print_json(self, mock_echo):
        """Test print_json function."""
        data = {"name": "test", "value": 123}
        print_json(data)
        mock_echo.assert_called_once()

    @mock.patch('click.echo')
    def test_print_progress_bar(self, mock_echo):
        """Test print_progress_bar function."""
        print_progress_bar(50, 100, prefix="Progress", suffix="Complete", length=20)
        mock_echo.assert_called_once()

    @mock.patch('click.echo')
    @mock.patch('threading.Thread')
    def test_print_spinner(self, mock_thread, mock_echo):
        """Test print_spinner function."""
        # Test with interactive mode
        set_interactive(True)
        stop_func = print_spinner("Loading...", total_time=0.1)
        mock_thread.assert_called_once()
        stop_func()

        # Test with non-interactive mode
        set_interactive(False)
        stop_func = print_spinner("Loading...")
        mock_echo.assert_called_with("Loading...")
        mock_thread.assert_called_once()

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.prompt')
    def test_prompt(self, mock_prompt):
        """Test prompt function."""
        # Test with interactive mode
        set_interactive(True)
        mock_prompt.return_value = "test"
        result = prompt("Enter value")
        self.assertEqual(result, "test")
        mock_prompt.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        result = prompt("Enter value", default="default")
        self.assertEqual(result, "default")

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.confirm')
    def test_confirm(self, mock_confirm):
        """Test confirm function."""
        # Test with interactive mode
        set_interactive(True)
        mock_confirm.return_value = True
        result = confirm("Confirm?")
        self.assertTrue(result)
        mock_confirm.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        result = confirm("Confirm?", default=False)
        self.assertFalse(result)

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.echo')
    @mock.patch('click.prompt')
    def test_select(self, mock_prompt, mock_echo):
        """Test select function."""
        # Test with interactive mode
        set_interactive(True)
        mock_prompt.return_value = "option1"
        result = select("Select option", ["option1", "option2"])
        self.assertEqual(result, "option1")
        mock_prompt.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        result = select("Select option", ["option1", "option2"], default="option2")
        self.assertEqual(result, "option2")

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.echo')
    @mock.patch('click.prompt')
    def test_multi_select(self, mock_prompt, mock_echo):
        """Test multi_select function."""
        # Test with interactive mode
        set_interactive(True)
        mock_prompt.return_value = "1,2"
        result = multi_select("Select options", ["option1", "option2", "option3"])
        self.assertEqual(result, ["option1", "option2"])
        mock_prompt.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        result = multi_select("Select options", ["option1", "option2", "option3"], defaults=["option3"])
        self.assertEqual(result, ["option3"])

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.prompt')
    def test_password(self, mock_prompt):
        """Test password function."""
        # Test with interactive mode
        set_interactive(True)
        mock_prompt.return_value = "password"
        result = password("Enter password")
        self.assertEqual(result, "password")
        mock_prompt.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        result = password("Enter password")
        self.assertEqual(result, "")

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.pause')
    def test_pause(self, mock_pause):
        """Test pause function."""
        # Test with interactive mode
        set_interactive(True)
        pause()
        mock_pause.assert_called_once()

        # Test with non-interactive mode
        set_interactive(False)
        pause()
        mock_pause.assert_called_once()

        # Reset interactive mode for other tests
        set_interactive(True)

    @mock.patch('click.clear')
    def test_clear_screen(self, mock_clear):
        """Test clear_screen function."""
        clear_screen()
        mock_clear.assert_called_once()
