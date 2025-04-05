"""
System and environment management module for HubQueue.
"""
import os
import sys
import platform
import subprocess
import shutil
import json
import tempfile
from pathlib import Path
from . import __version__
from .logging import get_logger

# Get logger
logger = get_logger()


def get_system_info():
    """
    Get system information.

    Returns:
        dict: System information
    """
    try:
        logger.debug("Getting system information")

        # Get system information
        system_info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_path": sys.executable,
        }

        # Get environment variables
        env_vars = {}
        for key, value in os.environ.items():
            # Skip sensitive environment variables
            if any(sensitive in key.lower() for sensitive in ["token", "key", "secret", "password", "auth"]):
                env_vars[key] = "***REDACTED***"
            else:
                env_vars[key] = value

        system_info["environment_variables"] = env_vars

        # Get installed packages
        try:
            import pkg_resources
            packages = []
            for package in pkg_resources.working_set:
                packages.append({
                    "name": package.project_name,
                    "version": package.version,
                })
            system_info["installed_packages"] = packages
        except ImportError:
            system_info["installed_packages"] = []

        # Get Git information
        try:
            git_version = subprocess.check_output(["git", "--version"], text=True).strip()
            system_info["git_version"] = git_version
        except (subprocess.SubprocessError, FileNotFoundError):
            system_info["git_version"] = "Git not found"

        logger.info("System information retrieved successfully")
        return system_info
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}")
        raise Exception(f"Error getting system information: {str(e)}")


def check_command_availability(command):
    """
    Check if a command is available in the system.

    Args:
        command (str): Command to check

    Returns:
        bool: True if command is available, False otherwise
    """
    try:
        logger.debug(f"Checking availability of command: {command}")

        # Check if command exists
        if platform.system() == "Windows":
            # On Windows, use where command
            result = subprocess.run(["where", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            # On Unix-like systems, use which command
            result = subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        available = result.returncode == 0

        logger.info(f"Command {command} is {'available' if available else 'not available'}")
        return available
    except Exception as e:
        logger.error(f"Error checking command availability: {str(e)}")
        return False


def check_git_config():
    """
    Check Git configuration.

    Returns:
        dict: Git configuration
    """
    try:
        logger.debug("Checking Git configuration")

        # Check if Git is available
        if not check_command_availability("git"):
            logger.error("Git is not available")
            return {"error": "Git is not available"}

        # Get Git configuration
        git_config = {}

        # Get user name
        try:
            git_config["user.name"] = subprocess.check_output(
                ["git", "config", "--get", "user.name"], text=True
            ).strip()
        except subprocess.SubprocessError:
            git_config["user.name"] = None

        # Get user email
        try:
            git_config["user.email"] = subprocess.check_output(
                ["git", "config", "--get", "user.email"], text=True
            ).strip()
        except subprocess.SubprocessError:
            git_config["user.email"] = None

        # Get default branch
        try:
            git_config["init.defaultBranch"] = subprocess.check_output(
                ["git", "config", "--get", "init.defaultBranch"], text=True
            ).strip()
        except subprocess.SubprocessError:
            git_config["init.defaultBranch"] = "master"  # Default value

        # Get credential helper
        try:
            git_config["credential.helper"] = subprocess.check_output(
                ["git", "config", "--get", "credential.helper"], text=True
            ).strip()
        except subprocess.SubprocessError:
            git_config["credential.helper"] = None

        # Get core editor
        try:
            git_config["core.editor"] = subprocess.check_output(
                ["git", "config", "--get", "core.editor"], text=True
            ).strip()
        except subprocess.SubprocessError:
            git_config["core.editor"] = None

        logger.info("Git configuration retrieved successfully")
        return git_config
    except Exception as e:
        logger.error(f"Error checking Git configuration: {str(e)}")
        raise Exception(f"Error checking Git configuration: {str(e)}")


def set_git_config(key, value, global_config=True):
    """
    Set Git configuration.

    Args:
        key (str): Configuration key
        value (str): Configuration value
        global_config (bool, optional): Whether to set global configuration. Defaults to True.

    Returns:
        bool: True if configuration was set successfully, False otherwise
    """
    try:
        logger.debug(f"Setting Git configuration: {key}={value} (global={global_config})")

        # Check if Git is available
        if not check_command_availability("git"):
            logger.error("Git is not available")
            return False

        # Set Git configuration
        cmd = ["git", "config"]
        if global_config:
            cmd.append("--global")
        cmd.extend([key, value])

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logger.info(f"Git configuration set successfully: {key}={value}")
            return True
        else:
            logger.error(f"Error setting Git configuration: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error setting Git configuration: {str(e)}")
        return False


def check_dependencies():
    """
    Check dependencies required by HubQueue.

    Returns:
        dict: Dependencies status
    """
    try:
        logger.debug("Checking dependencies")

        dependencies = {
            "git": check_command_availability("git"),
        }

        # Check Python packages
        try:
            import github
            dependencies["PyGithub"] = True
        except ImportError:
            dependencies["PyGithub"] = False

        try:
            import click
            dependencies["click"] = True
        except ImportError:
            dependencies["click"] = False

        try:
            import requests
            dependencies["requests"] = True
        except ImportError:
            dependencies["requests"] = False

        try:
            import dotenv
            dependencies["python-dotenv"] = True
        except ImportError:
            dependencies["python-dotenv"] = False

        try:
            import colorama
            dependencies["colorama"] = True
        except ImportError:
            dependencies["colorama"] = False

        try:
            import tabulate
            dependencies["tabulate"] = True
        except ImportError:
            dependencies["tabulate"] = False

        try:
            import tqdm
            dependencies["tqdm"] = True
        except ImportError:
            dependencies["tqdm"] = False

        try:
            import jinja2
            dependencies["jinja2"] = True
        except ImportError:
            dependencies["jinja2"] = False

        logger.info("Dependencies checked successfully")
        return dependencies
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        raise Exception(f"Error checking dependencies: {str(e)}")


def install_dependency(dependency, upgrade=False):
    """
    Install a dependency.

    Args:
        dependency (str): Dependency to install
        upgrade (bool, optional): Whether to upgrade the dependency. Defaults to False.

    Returns:
        bool: True if installation was successful, False otherwise
    """
    try:
        logger.debug(f"Installing dependency: {dependency} (upgrade={upgrade})")

        # Check if pip is available
        if not check_command_availability("pip"):
            logger.error("pip is not available")
            return False

        # Install dependency
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(dependency)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logger.info(f"Dependency {dependency} installed successfully")
            return True
        else:
            logger.error(f"Error installing dependency {dependency}: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing dependency: {str(e)}")
        return False


def check_windows_compatibility():
    """
    Check Windows compatibility.

    Returns:
        dict: Windows compatibility status
    """
    try:
        logger.debug("Checking Windows compatibility")

        # Check if running on Windows
        if platform.system() != "Windows":
            logger.info("Not running on Windows")
            return {"is_windows": False}

        compatibility = {
            "is_windows": True,
            "windows_version": platform.version(),
            "windows_release": platform.release(),
            "windows_edition": platform.win32_edition() if hasattr(platform, "win32_edition") else "Unknown",
        }

        # Check if running in WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    compatibility["is_wsl"] = True
                else:
                    compatibility["is_wsl"] = False
        except FileNotFoundError:
            compatibility["is_wsl"] = False

        # Check if running in PowerShell
        compatibility["is_powershell"] = "POWERSHELL_DISTRIBUTION_CHANNEL" in os.environ

        # Check if running in Command Prompt
        compatibility["is_cmd"] = "PROMPT" in os.environ and not compatibility["is_powershell"]

        # Check if Git Bash is available
        compatibility["git_bash_available"] = shutil.which("bash.exe") is not None

        logger.info("Windows compatibility checked successfully")
        return compatibility
    except Exception as e:
        logger.error(f"Error checking Windows compatibility: {str(e)}")
        raise Exception(f"Error checking Windows compatibility: {str(e)}")


def setup_windows_environment():
    """
    Setup Windows environment for HubQueue.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        logger.debug("Setting up Windows environment")

        # Check if running on Windows
        if platform.system() != "Windows":
            logger.error("Not running on Windows")
            return False

        # Enable ANSI color support in Windows console
        try:
            # Try to import colorama
            try:
                import colorama
                colorama.init()
                logger.info("ANSI color support enabled")
            except ImportError:
                logger.warning("colorama not installed, ANSI color support not enabled")
        except Exception as e:
            logger.warning(f"Error initializing colorama: {str(e)}")

        # Set up Git credential manager
        if check_command_availability("git"):
            # Check if credential manager is already configured
            git_config = check_git_config()
            if not git_config.get("credential.helper"):
                # Set up Git credential manager
                set_git_config("credential.helper", "manager-core")
                logger.info("Git credential manager configured")

        logger.info("Windows environment setup completed")
        return True
    except Exception as e:
        logger.error(f"Error setting up Windows environment: {str(e)}")
        return False


def setup_unix_environment():
    """
    Setup Unix environment for HubQueue.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        logger.debug("Setting up Unix environment")

        # Check if running on Unix-like system
        if platform.system() == "Windows":
            logger.error("Not running on Unix-like system")
            return False

        # Set up Git credential manager
        if check_command_availability("git"):
            # Check if credential manager is already configured
            git_config = check_git_config()
            if not git_config.get("credential.helper"):
                # Set up Git credential manager based on platform
                if platform.system() == "Darwin":  # macOS
                    set_git_config("credential.helper", "osxkeychain")
                    logger.info("Git credential manager configured (osxkeychain)")
                else:  # Linux and other Unix-like systems
                    # Try to use libsecret if available
                    if os.path.exists("/usr/share/doc/git/contrib/credential/libsecret"):
                        set_git_config("credential.helper", "/usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret")
                        logger.info("Git credential manager configured (libsecret)")
                    else:
                        # Fall back to cache
                        set_git_config("credential.helper", "cache --timeout=3600")
                        logger.info("Git credential manager configured (cache)")

        logger.info("Unix environment setup completed")
        return True
    except Exception as e:
        logger.error(f"Error setting up Unix environment: {str(e)}")
        return False


def setup_environment():
    """
    Setup environment for HubQueue based on the platform.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        logger.debug("Setting up environment")

        # Setup environment based on platform
        if platform.system() == "Windows":
            result = setup_windows_environment()
        else:
            result = setup_unix_environment()

        logger.info(f"Environment setup {'completed successfully' if result else 'failed'}")
        return result
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        return False


def export_environment(output_file=None):
    """
    Export environment information to a file.

    Args:
        output_file (str, optional): Output file path. If None, a temporary file will be created.

    Returns:
        str: Path to the output file
    """
    try:
        logger.debug(f"Exporting environment information to {output_file or 'temporary file'}")

        # Get environment information
        env_info = {
            "system_info": get_system_info(),
            "git_config": check_git_config(),
            "dependencies": check_dependencies(),
        }

        # Add Windows compatibility information if on Windows
        if platform.system() == "Windows":
            env_info["windows_compatibility"] = check_windows_compatibility()

        # Create output file
        if output_file:
            file_path = output_file
        else:
            # Create temporary file
            fd, file_path = tempfile.mkstemp(suffix=".json", prefix="hubqueue_env_")
            os.close(fd)

        # Write environment information to file
        with open(file_path, "w") as f:
            json.dump(env_info, f, indent=2)

        logger.info(f"Environment information exported to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error exporting environment information: {str(e)}")
        raise Exception(f"Error exporting environment information: {str(e)}")


def check_for_updates():
    """
    Check for updates to HubQueue.

    Returns:
        dict: Update information
    """
    try:
        logger.debug("Checking for updates")

        # Get current version
        try:
            from . import __version__
            current_version = __version__
        except ImportError:
            current_version = "unknown"

        # Check for updates using pip
        try:
            import requests
            response = requests.get("https://pypi.org/pypi/hubqueue/json")
            if response.status_code == 200:
                data = response.json()
                latest_version = data["info"]["version"]

                # Compare versions
                update_available = latest_version != current_version

                logger.info(f"Update check completed: current={current_version}, latest={latest_version}, update_available={update_available}")
                return {
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "update_available": update_available,
                }
            else:
                logger.warning(f"Error checking for updates: HTTP {response.status_code}")
                return {
                    "current_version": current_version,
                    "error": f"HTTP {response.status_code}",
                }
        except Exception as e:
            logger.warning(f"Error checking for updates: {str(e)}")
            return {
                "current_version": current_version,
                "error": str(e),
            }
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        raise Exception(f"Error checking for updates: {str(e)}")


def update_hubqueue(upgrade=True):
    """
    Update HubQueue to the latest version.

    Args:
        upgrade (bool, optional): Whether to upgrade dependencies. Defaults to True.

    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        logger.debug(f"Updating HubQueue (upgrade={upgrade})")

        # Check if pip is available
        if not check_command_availability("pip"):
            logger.error("pip is not available")
            return False

        # Update HubQueue
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "hubqueue"]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logger.info("HubQueue updated successfully")
            return True
        else:
            logger.error(f"Error updating HubQueue: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error updating HubQueue: {str(e)}")
        return False
