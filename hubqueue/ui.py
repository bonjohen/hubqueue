"""
User interface module for HubQueue.
"""
import os
import sys
import time
import json
import platform
import shutil
import click
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Union
from .logging import get_logger

# Get logger
logger = get_logger()

# Define color constants
class Color(Enum):
    """Color constants for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Bright background colors
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"


# Global variables
_use_color = True
_terminal_width = None
_interactive = True


def init_ui():
    """
    Initialize the UI module.
    """
    global _use_color, _terminal_width, _interactive

    # Check if color is supported
    _use_color = _supports_color()

    # Get terminal width
    _terminal_width = _get_terminal_width()

    # Check if interactive
    _interactive = _is_interactive()

    # Initialize colorama if on Windows
    if platform.system() == "Windows" and _use_color:
        try:
            import colorama
            colorama.init()
        except ImportError:
            _use_color = False
            logger.warning("colorama not installed, disabling color support")


def _supports_color():
    """
    Check if the terminal supports color.

    Returns:
        bool: True if color is supported, False otherwise
    """
    # Check if NO_COLOR environment variable is set
    if os.environ.get("NO_COLOR") is not None:
        return False

    # Check if FORCE_COLOR environment variable is set
    if os.environ.get("FORCE_COLOR") is not None:
        return True

    # Check if running in a terminal
    if not sys.stdout.isatty():
        return False

    # Check platform-specific conditions
    if platform.system() == "Windows":
        # Check if running in Windows Terminal, VSCode, or other modern terminal
        if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"):
            return True

        # Check Windows version
        if sys.getwindowsversion().major >= 10:
            return True

        # Check if ANSICON environment variable is set
        if os.environ.get("ANSICON") is not None:
            return True

        return False

    # Check if TERM environment variable is set
    if os.environ.get("TERM") == "dumb":
        return False

    return True


def _get_terminal_width():
    """
    Get the terminal width.

    Returns:
        int: Terminal width in characters
    """
    try:
        return shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        return 80


def _is_interactive():
    """
    Check if the terminal is interactive.

    Returns:
        bool: True if interactive, False otherwise
    """
    # Check if stdin and stdout are TTYs
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return False

    # Check if running in a CI environment
    if os.environ.get("CI") is not None:
        return False

    return True


def set_color(enabled=True):
    """
    Enable or disable color output.

    Args:
        enabled (bool, optional): Whether to enable color output. Defaults to True.
    """
    global _use_color
    _use_color = enabled and _supports_color()


def set_interactive(enabled=True):
    """
    Enable or disable interactive mode.

    Args:
        enabled (bool, optional): Whether to enable interactive mode. Defaults to True.
    """
    global _interactive
    _interactive = enabled and _is_interactive()


def is_interactive():
    """
    Check if interactive mode is enabled.

    Returns:
        bool: True if interactive mode is enabled, False otherwise
    """
    return _interactive


def is_color_enabled():
    """
    Check if color output is enabled.

    Returns:
        bool: True if color output is enabled, False otherwise
    """
    return _use_color


def get_terminal_width():
    """
    Get the terminal width.

    Returns:
        int: Terminal width in characters
    """
    global _terminal_width
    _terminal_width = _get_terminal_width()
    return _terminal_width


def colorize(text, color=None, background=None, bold=False, dim=False, italic=False, underline=False, blink=False, reverse=False):
    """
    Colorize text for terminal output.

    Args:
        text (str): Text to colorize
        color (Color, optional): Foreground color. Defaults to None.
        background (Color, optional): Background color. Defaults to None.
        bold (bool, optional): Whether to make text bold. Defaults to False.
        dim (bool, optional): Whether to make text dim. Defaults to False.
        italic (bool, optional): Whether to make text italic. Defaults to False.
        underline (bool, optional): Whether to underline text. Defaults to False.
        blink (bool, optional): Whether to make text blink. Defaults to False.
        reverse (bool, optional): Whether to reverse text colors. Defaults to False.

    Returns:
        str: Colorized text
    """
    if not _use_color:
        return text

    # Build color string
    color_str = ""

    if bold:
        color_str += Color.BOLD.value

    if dim:
        color_str += Color.DIM.value

    if italic:
        color_str += Color.ITALIC.value

    if underline:
        color_str += Color.UNDERLINE.value

    if blink:
        color_str += Color.BLINK.value

    if reverse:
        color_str += Color.REVERSE.value

    if color:
        if isinstance(color, Color):
            color_str += color.value
        else:
            color_str += color

    if background:
        if isinstance(background, Color):
            color_str += background.value
        else:
            color_str += background

    # Return colorized text
    return f"{color_str}{text}{Color.RESET.value}"


def print_color(text, color=None, background=None, bold=False, dim=False, italic=False, underline=False, blink=False, reverse=False, end="\n"):
    """
    Print colorized text to the terminal.

    Args:
        text (str): Text to print
        color (Color, optional): Foreground color. Defaults to None.
        background (Color, optional): Background color. Defaults to None.
        bold (bool, optional): Whether to make text bold. Defaults to False.
        dim (bool, optional): Whether to make text dim. Defaults to False.
        italic (bool, optional): Whether to make text italic. Defaults to False.
        underline (bool, optional): Whether to underline text. Defaults to False.
        blink (bool, optional): Whether to make text blink. Defaults to False.
        reverse (bool, optional): Whether to reverse text colors. Defaults to False.
        end (str, optional): String to append after text. Defaults to "\n".
    """
    click.echo(colorize(text, color, background, bold, dim, italic, underline, blink, reverse), nl=False)
    click.echo(end, nl=False)


def print_info(text, bold=False):
    """
    Print informational text to the terminal.

    Args:
        text (str): Text to print
        bold (bool, optional): Whether to make text bold. Defaults to False.
    """
    print_color(text, Color.CYAN, bold=bold)


def print_success(text, bold=False):
    """
    Print success text to the terminal.

    Args:
        text (str): Text to print
        bold (bool, optional): Whether to make text bold. Defaults to False.
    """
    print_color(text, Color.GREEN, bold=bold)


def print_warning(text, bold=False):
    """
    Print warning text to the terminal.

    Args:
        text (str): Text to print
        bold (bool, optional): Whether to make text bold. Defaults to False.
    """
    print_color(text, Color.YELLOW, bold=bold)


def print_error(text, bold=False):
    """
    Print error text to the terminal.

    Args:
        text (str): Text to print
        bold (bool, optional): Whether to make text bold. Defaults to False.
    """
    print_color(text, Color.RED, bold=bold)


def print_debug(text, bold=False):
    """
    Print debug text to the terminal.

    Args:
        text (str): Text to print
        bold (bool, optional): Whether to make text bold. Defaults to False.
    """
    print_color(text, Color.MAGENTA, bold=bold)


def print_header(text, width=None, char="=", color=Color.CYAN, bold=True):
    """
    Print a header to the terminal.

    Args:
        text (str): Header text
        width (int, optional): Header width. Defaults to terminal width.
        char (str, optional): Character to use for the header line. Defaults to "=".
        color (Color, optional): Header color. Defaults to Color.CYAN.
        bold (bool, optional): Whether to make header bold. Defaults to True.
    """
    width = width or _terminal_width

    # Calculate padding
    padding = max(0, width - len(text) - 4)
    left_padding = padding // 2
    right_padding = padding - left_padding

    # Print header
    print_color(char * width, color, bold=bold)
    print_color(f"{char * 2}{' ' * left_padding}{text}{' ' * right_padding}{char * 2}", color, bold=bold)
    print_color(char * width, color, bold=bold)


def print_table(headers, rows, color=Color.CYAN, header_color=Color.CYAN, header_bold=True, border=True):
    """
    Print a table to the terminal.

    Args:
        headers (List[str]): Table headers
        rows (List[List[str]]): Table rows
        color (Color, optional): Table color. Defaults to Color.CYAN.
        header_color (Color, optional): Header color. Defaults to Color.CYAN.
        header_bold (bool, optional): Whether to make headers bold. Defaults to True.
        border (bool, optional): Whether to draw table borders. Defaults to True.
    """
    if not headers or not rows:
        return

    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Calculate total width
    total_width = sum(col_widths) + len(col_widths) * 3 - 1

    # Print top border
    if border:
        print_color("+" + "-" * (total_width - 2) + "+", color)

    # Print headers
    header_row = "| "
    for i, header in enumerate(headers):
        header_text = str(header).ljust(col_widths[i])
        if _use_color:
            header_text = colorize(header_text, header_color, bold=header_bold)
        header_row += header_text + " | "
    print_color(header_row, color)

    # Print header separator
    if border:
        separator = "+"
        for width in col_widths:
            separator += "-" * (width + 2) + "+"
        print_color(separator, color)

    # Print rows
    for row in rows:
        row_text = "| "
        for i, cell in enumerate(row):
            if i < len(col_widths):
                row_text += str(cell).ljust(col_widths[i]) + " | "
        print_color(row_text, color)

    # Print bottom border
    if border:
        print_color("+" + "-" * (total_width - 2) + "+", color)


def print_json(data, indent=2, color=True):
    """
    Print JSON data to the terminal.

    Args:
        data (Any): Data to print as JSON
        indent (int, optional): JSON indentation. Defaults to 2.
        color (bool, optional): Whether to colorize output. Defaults to True.
    """
    json_str = json.dumps(data, indent=indent)

    if color and _use_color:
        # Colorize JSON
        json_str = json_str.replace('"', f'{Color.GREEN.value}"')
        json_str = json_str.replace('": ', f'"{Color.RESET.value}: {Color.YELLOW.value}')
        json_str = json_str.replace(",", f"{Color.RESET.value},")
        json_str = json_str.replace("}", f"{Color.RESET.value}}}")
        json_str = json_str.replace("]", f"{Color.RESET.value}]")
        json_str += Color.RESET.value

    click.echo(json_str)


def print_progress_bar(iteration, total, prefix="", suffix="", decimals=1, length=None, fill="█", color=Color.CYAN):
    """
    Print a progress bar to the terminal.

    Args:
        iteration (int): Current iteration
        total (int): Total iterations
        prefix (str, optional): Prefix string. Defaults to "".
        suffix (str, optional): Suffix string. Defaults to "".
        decimals (int, optional): Decimal places for percentage. Defaults to 1.
        length (int, optional): Character length of bar. Defaults to terminal width - 10.
        fill (str, optional): Bar fill character. Defaults to "█".
        color (Color, optional): Bar color. Defaults to Color.CYAN.
    """
    if total <= 0:
        return

    # Calculate length
    length = length or (_terminal_width - len(prefix) - len(suffix) - 10)
    length = max(10, length)

    # Calculate percentage and filled length
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)

    # Create bar
    bar = fill * filled_length + "-" * (length - filled_length)

    # Print progress bar
    progress_text = f"\r{prefix} |{bar}| {percent}% {suffix}"
    if _use_color:
        progress_text = colorize(progress_text, color)

    click.echo(progress_text, nl=False)

    # Print new line on complete
    if iteration >= total:
        click.echo()


def print_spinner(text="Loading...", spinner_type="dots", color=Color.CYAN, delay=0.1, total_time=None):
    """
    Print a spinner to the terminal.

    Args:
        text (str, optional): Text to display. Defaults to "Loading...".
        spinner_type (str, optional): Spinner type. Defaults to "dots".
        color (Color, optional): Spinner color. Defaults to Color.CYAN.
        delay (float, optional): Delay between spinner frames. Defaults to 0.1.
        total_time (float, optional): Total time to display spinner. Defaults to None.

    Returns:
        callable: Function to stop the spinner
    """
    if not _interactive:
        click.echo(text)
        return lambda: None

    # Define spinner frames
    spinners = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["|", "/", "-", "\\"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "pulse": ["█", "▓", "▒", "░"],
    }

    frames = spinners.get(spinner_type, spinners["dots"])

    # Initialize variables
    start_time = time.time()
    stop_spinner = False

    def stop():
        nonlocal stop_spinner
        stop_spinner = True
        click.echo()

    # Start spinner in a separate thread
    import threading

    def spin():
        i = 0
        while not stop_spinner:
            frame = frames[i % len(frames)]
            spinner_text = f"\r{frame} {text}"

            if _use_color:
                spinner_text = colorize(spinner_text, color)

            click.echo(spinner_text, nl=False)

            time.sleep(delay)
            i += 1

            # Check if total time has elapsed
            if total_time and time.time() - start_time >= total_time:
                stop()
                break

    spinner_thread = threading.Thread(target=spin)
    spinner_thread.daemon = True
    spinner_thread.start()

    return stop


def prompt(text, default=None, type=str, validate=None, color=Color.CYAN, show_default=True):
    """
    Prompt the user for input.

    Args:
        text (str): Prompt text
        default (Any, optional): Default value. Defaults to None.
        type (type, optional): Input type. Defaults to str.
        validate (callable, optional): Validation function. Defaults to None.
        color (Color, optional): Prompt color. Defaults to Color.CYAN.
        show_default (bool, optional): Whether to show default value. Defaults to True.

    Returns:
        Any: User input
    """
    if not _interactive:
        return default

    # Format prompt text
    prompt_text = text
    if default is not None and show_default:
        prompt_text = f"{text} [{default}]"

    # Colorize prompt
    if _use_color:
        prompt_text = colorize(prompt_text, color)

    # Prompt for input
    while True:
        try:
            value = click.prompt(prompt_text, default=default, type=type, show_default=False)

            # Validate input
            if validate and not validate(value):
                print_error("Invalid input. Please try again.")
                continue

            return value
        except click.Abort:
            raise
        except Exception as e:
            print_error(f"Error: {str(e)}")


def confirm(text, default=False, color=Color.CYAN, abort=False):
    """
    Prompt the user for confirmation.

    Args:
        text (str): Prompt text
        default (bool, optional): Default value. Defaults to False.
        color (Color, optional): Prompt color. Defaults to Color.CYAN.
        abort (bool, optional): Whether to abort on negative response. Defaults to False.

    Returns:
        bool: True if confirmed, False otherwise
    """
    if not _interactive:
        return default

    # Colorize prompt
    if _use_color:
        text = colorize(text, color)

    # Prompt for confirmation
    try:
        return click.confirm(text, default=default, abort=abort)
    except click.Abort:
        raise
    except Exception:
        return default


def select(text, options, default=None, color=Color.CYAN, show_default=True):
    """
    Prompt the user to select from a list of options.

    Args:
        text (str): Prompt text
        options (List[str]): Options to select from
        default (str, optional): Default value. Defaults to None.
        color (Color, optional): Prompt color. Defaults to Color.CYAN.
        show_default (bool, optional): Whether to show default value. Defaults to True.

    Returns:
        str: Selected option
    """
    if not _interactive or not options:
        return default if default is not None else options[0] if options else None

    # Format prompt text
    prompt_text = text
    if default is not None and show_default:
        prompt_text = f"{text} [{default}]"

    # Colorize prompt
    if _use_color:
        prompt_text = colorize(prompt_text, color)

    # Display options
    for i, option in enumerate(options):
        option_text = f"{i + 1}. {option}"
        if option == default:
            option_text += " (default)"

        click.echo(option_text)

    # Prompt for selection
    while True:
        try:
            value = click.prompt(prompt_text, default=default, show_default=False)

            # Check if input is a number
            try:
                index = int(value) - 1
                if 0 <= index < len(options):
                    return options[index]
            except ValueError:
                pass

            # Check if input matches an option
            if value in options:
                return value

            # Use default if input is empty
            if not value and default is not None:
                return default

            print_error("Invalid selection. Please try again.")
        except click.Abort:
            raise
        except Exception as e:
            print_error(f"Error: {str(e)}")


def multi_select(text, options, defaults=None, color=Color.CYAN):
    """
    Prompt the user to select multiple options from a list.

    Args:
        text (str): Prompt text
        options (List[str]): Options to select from
        defaults (List[str], optional): Default selected options. Defaults to None.
        color (Color, optional): Prompt color. Defaults to Color.CYAN.

    Returns:
        List[str]: Selected options
    """
    if not _interactive or not options:
        return defaults or []

    # Initialize defaults
    defaults = defaults or []

    # Colorize prompt
    prompt_text = text
    if _use_color:
        prompt_text = colorize(prompt_text, color)

    # Display options
    click.echo(prompt_text)
    for i, option in enumerate(options):
        option_text = f"{i + 1}. {option}"
        if option in defaults:
            option_text += " (selected)"

        click.echo(option_text)

    # Prompt for selection
    click.echo("Enter numbers separated by commas, or 'all' to select all, or 'none' to select none.")

    while True:
        try:
            value = click.prompt("Selection", default="", show_default=False)

            # Check for special values
            if value.lower() == "all":
                return options
            elif value.lower() == "none":
                return []

            # Parse selection
            selected = []
            for part in value.split(","):
                part = part.strip()

                # Check if input is a number
                try:
                    index = int(part) - 1
                    if 0 <= index < len(options):
                        selected.append(options[index])
                except ValueError:
                    # Check if input matches an option
                    if part in options:
                        selected.append(part)

            return selected
        except click.Abort:
            raise
        except Exception as e:
            print_error(f"Error: {str(e)}")


def password(text, confirmation_prompt=True, color=Color.CYAN):
    """
    Prompt the user for a password.

    Args:
        text (str): Prompt text
        confirmation_prompt (bool, optional): Whether to prompt for confirmation. Defaults to True.
        color (Color, optional): Prompt color. Defaults to Color.CYAN.

    Returns:
        str: Password
    """
    if not _interactive:
        return ""

    # Colorize prompt
    if _use_color:
        text = colorize(text, color)

    # Prompt for password
    try:
        return click.prompt(text, hide_input=True, confirmation_prompt=confirmation_prompt)
    except click.Abort:
        raise
    except Exception:
        return ""


def pause(text="Press any key to continue...", color=Color.CYAN):
    """
    Pause execution until the user presses a key.

    Args:
        text (str, optional): Prompt text. Defaults to "Press any key to continue...".
        color (Color, optional): Prompt color. Defaults to Color.CYAN.
    """
    if not _interactive:
        return

    # Colorize prompt
    if _use_color:
        text = colorize(text, color)

    # Prompt for key press
    click.pause(info=text)


def clear_screen():
    """
    Clear the terminal screen.
    """
    click.clear()


def get_editor():
    """
    Get the default text editor.

    Returns:
        str: Default text editor
    """
    return click.get_editor()


def edit(text=None, extension=".txt", require_save=True):
    """
    Open the default text editor.

    Args:
        text (str, optional): Initial text. Defaults to None.
        extension (str, optional): File extension. Defaults to ".txt".
        require_save (bool, optional): Whether to require saving. Defaults to True.

    Returns:
        str: Edited text
    """
    if not _interactive:
        return text or ""

    try:
        return click.edit(text, extension=extension, require_save=require_save)
    except click.Abort:
        raise
    except Exception:
        return text or ""


def launch(command, echo=False):
    """
    Launch a command in a new process.

    Args:
        command (str): Command to launch
        echo (bool, optional): Whether to echo the command. Defaults to False.

    Returns:
        int: Exit code
    """
    if echo:
        click.echo(f"$ {command}")

    return click.launch(command)


def open_url(url, echo=False):
    """
    Open a URL in the default web browser.

    Args:
        url (str): URL to open
        echo (bool, optional): Whether to echo the URL. Defaults to False.

    Returns:
        int: Exit code
    """
    if echo:
        click.echo(f"Opening {url}")

    return click.launch(url)


# Initialize UI module
init_ui()
