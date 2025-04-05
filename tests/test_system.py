"""
Tests for the system module.
"""
import os
import sys
import platform
import tempfile
import json
import subprocess
from unittest import TestCase, mock

from hubqueue.system import (
    get_system_info, check_command_availability, check_git_config,
    set_git_config, check_dependencies, install_dependency,
    check_windows_compatibility, setup_windows_environment,
    setup_unix_environment, setup_environment, export_environment,
    check_for_updates, update_hubqueue
)


class TestSystem(TestCase):
    """Test system and environment management functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()

        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_system_info(self):
        """Test getting system information."""
        # Mock subprocess.check_output for Git version
        with mock.patch("subprocess.check_output") as mock_check_output:
            mock_check_output.return_value = "git version 2.30.0"

            # Get system information
            info = get_system_info()

            # Verify result
            self.assertEqual(info["os"], platform.system())
            self.assertEqual(info["os_release"], platform.release())
            self.assertEqual(info["os_version"], platform.version())
            self.assertEqual(info["architecture"], platform.machine())
            self.assertEqual(info["processor"], platform.processor())
            self.assertEqual(info["python_version"], platform.python_version())
            self.assertEqual(info["python_implementation"], platform.python_implementation())
            self.assertEqual(info["python_path"], sys.executable)
            self.assertEqual(info["git_version"], "git version 2.30.0")
            self.assertIn("environment_variables", info)
            self.assertIn("installed_packages", info)

    def test_check_command_availability_available(self):
        """Test checking command availability when command is available."""
        # Mock subprocess.run
        with mock.patch("subprocess.run") as mock_run:
            mock_result = mock.MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Check command availability
            result = check_command_availability("git")

            # Verify result
            self.assertTrue(result)
            mock_run.assert_called_once()

    def test_check_command_availability_not_available(self):
        """Test checking command availability when command is not available."""
        # Mock subprocess.run
        with mock.patch("subprocess.run") as mock_run:
            mock_result = mock.MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            # Check command availability
            result = check_command_availability("nonexistent-command")

            # Verify result
            self.assertFalse(result)
            mock_run.assert_called_once()

    def test_check_git_config(self):
        """Test checking Git configuration."""
        # Mock check_command_availability
        with mock.patch("hubqueue.system.check_command_availability") as mock_check:
            mock_check.return_value = True

            # Mock subprocess.check_output
            with mock.patch("subprocess.check_output") as mock_check_output:
                # Set return value for each command
                mock_check_output.side_effect = lambda cmd, **kwargs: {
                    "git config --get user.name": "Test User",
                    "git config --get user.email": "test@example.com",
                    "git config --get init.defaultBranch": "main",
                    "git config --get credential.helper": "manager-core",
                    "git config --get core.editor": "vim"
                }.get(" ".join(cmd), "")

                # Check Git configuration
                config = check_git_config()

                # Verify result
                self.assertEqual(config["user.name"], "Test User")
                self.assertEqual(config["user.email"], "test@example.com")
                self.assertEqual(config["init.defaultBranch"], "main")
                self.assertEqual(config["credential.helper"], "manager-core")
                self.assertEqual(config["core.editor"], "vim")

    def test_set_git_config(self):
        """Test setting Git configuration."""
        # Mock check_command_availability
        with mock.patch("hubqueue.system.check_command_availability") as mock_check:
            mock_check.return_value = True

            # Mock subprocess.run
            with mock.patch("subprocess.run") as mock_run:
                mock_result = mock.MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                # Set Git configuration
                result = set_git_config("user.name", "Test User", True)

                # Verify result
                self.assertTrue(result)
                mock_run.assert_called_once_with(
                    ["git", "config", "--global", "user.name", "Test User"],
                    stdout=mock.ANY, stderr=mock.ANY, text=True
                )

    def test_check_dependencies(self):
        """Test checking dependencies."""
        # Mock check_command_availability
        with mock.patch("hubqueue.system.check_command_availability") as mock_check:
            mock_check.return_value = True

            # Check dependencies
            dependencies = check_dependencies()

            # Verify result
            self.assertIn("git", dependencies)
            self.assertIn("PyGithub", dependencies)
            self.assertIn("click", dependencies)
            self.assertIn("requests", dependencies)
            self.assertIn("python-dotenv", dependencies)
            self.assertIn("colorama", dependencies)
            self.assertIn("tabulate", dependencies)
            self.assertIn("tqdm", dependencies)
            self.assertIn("jinja2", dependencies)

    @mock.patch("hubqueue.system.subprocess.run")
    def test_install_dependency(self, mock_run):
        """Test installing a dependency."""
        # Mock subprocess.run
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Mock check_command_availability
        with mock.patch("hubqueue.system.check_command_availability") as mock_check:
            mock_check.return_value = True

            # Install dependency
            result = install_dependency("click")

            # Verify result
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                [sys.executable, "-m", "pip", "install", "click"],
                stdout=mock.ANY, stderr=mock.ANY, text=True
            )

    def test_check_windows_compatibility_not_windows(self):
        """Test checking Windows compatibility when not on Windows."""
        # Mock platform.system
        with mock.patch("platform.system") as mock_system:
            mock_system.return_value = "Linux"

            # Check Windows compatibility
            compatibility = check_windows_compatibility()

            # Verify result
            self.assertFalse(compatibility["is_windows"])

    @mock.patch("platform.system")
    @mock.patch("platform.version")
    @mock.patch("platform.release")
    @mock.patch("shutil.which")
    def test_check_windows_compatibility_windows(self, mock_which, mock_release, mock_version, mock_system):
        """Test checking Windows compatibility when on Windows."""
        # Mock platform functions
        mock_system.return_value = "Windows"
        mock_version.return_value = "10.0.19042"
        mock_release.return_value = "10"

        # Mock shutil.which
        mock_which.return_value = "C:\\Program Files\\Git\\bin\\bash.exe"

        # Mock environment variables
        with mock.patch.dict(os.environ, {"POWERSHELL_DISTRIBUTION_CHANNEL": "Microsoft.PowerShell"}):
            # Check Windows compatibility
            compatibility = check_windows_compatibility()

            # Verify result
            self.assertTrue(compatibility["is_windows"])
            self.assertEqual(compatibility["windows_version"], "10.0.19042")
            self.assertEqual(compatibility["windows_release"], "10")
            self.assertTrue(compatibility["is_powershell"])
            self.assertFalse(compatibility["is_cmd"])
            self.assertTrue(compatibility["git_bash_available"])

    @mock.patch("platform.system")
    @mock.patch("hubqueue.system.check_command_availability")
    @mock.patch("hubqueue.system.check_git_config")
    @mock.patch("hubqueue.system.set_git_config")
    def test_setup_windows_environment(self, mock_set_config, mock_check_config, mock_check_cmd, mock_system):
        """Test setting up Windows environment."""
        # Mock platform.system
        mock_system.return_value = "Windows"

        # Mock check_command_availability
        mock_check_cmd.return_value = True

        # Mock check_git_config
        mock_check_config.return_value = {"credential.helper": None}

        # Setup Windows environment
        result = setup_windows_environment()

        # Verify result
        self.assertTrue(result)
        mock_set_config.assert_called_once_with("credential.helper", "manager-core")

    @mock.patch("platform.system")
    @mock.patch("hubqueue.system.check_command_availability")
    @mock.patch("hubqueue.system.check_git_config")
    @mock.patch("hubqueue.system.set_git_config")
    def test_setup_unix_environment_macos(self, mock_set_config, mock_check_config, mock_check_cmd, mock_system):
        """Test setting up Unix environment on macOS."""
        # Mock platform.system
        mock_system.side_effect = ["Darwin", "Darwin"]  # First for Windows check, second for macOS check

        # Mock check_command_availability
        mock_check_cmd.return_value = True

        # Mock check_git_config
        mock_check_config.return_value = {"credential.helper": None}

        # Setup Unix environment
        result = setup_unix_environment()

        # Verify result
        self.assertTrue(result)
        mock_set_config.assert_called_once_with("credential.helper", "osxkeychain")

    @mock.patch("platform.system")
    def test_setup_environment_windows(self, mock_system):
        """Test setting up environment on Windows."""
        # Mock platform.system
        mock_system.return_value = "Windows"

        # Mock setup_windows_environment
        with mock.patch("hubqueue.system.setup_windows_environment") as mock_setup:
            mock_setup.return_value = True

            # Setup environment
            result = setup_environment()

            # Verify result
            self.assertTrue(result)
            mock_setup.assert_called_once()

    @mock.patch("platform.system")
    def test_setup_environment_unix(self, mock_system):
        """Test setting up environment on Unix-like system."""
        # Mock platform.system
        mock_system.return_value = "Linux"

        # Mock setup_unix_environment
        with mock.patch("hubqueue.system.setup_unix_environment") as mock_setup:
            mock_setup.return_value = True

            # Setup environment
            result = setup_environment()

            # Verify result
            self.assertTrue(result)
            mock_setup.assert_called_once()

    def test_export_environment(self):
        """Test exporting environment information."""
        # Mock get_system_info
        with mock.patch("hubqueue.system.get_system_info") as mock_get_info:
            mock_get_info.return_value = {"os": "Windows", "python_version": "3.9.0"}

            # Mock check_git_config
            with mock.patch("hubqueue.system.check_git_config") as mock_check_git:
                mock_check_git.return_value = {"user.name": "Test User"}

                # Mock check_dependencies
                with mock.patch("hubqueue.system.check_dependencies") as mock_check_deps:
                    mock_check_deps.return_value = {"git": True, "PyGithub": True}

                    # Export environment
                    output_file = os.path.join(self.temp_dir, "env.json")
                    file_path = export_environment(output_file)

                    # Verify result
                    self.assertEqual(file_path, output_file)
                    self.assertTrue(os.path.exists(output_file))

                    # Check file content
                    with open(output_file, "r") as f:
                        env_info = json.load(f)
                        self.assertEqual(env_info["system_info"]["os"], "Windows")
                        self.assertEqual(env_info["system_info"]["python_version"], "3.9.0")
                        self.assertEqual(env_info["git_config"]["user.name"], "Test User")
                        self.assertEqual(env_info["dependencies"]["git"], True)
                        self.assertEqual(env_info["dependencies"]["PyGithub"], True)

    @mock.patch("requests.get")
    def test_check_for_updates(self, mock_get):
        """Test checking for updates."""
        # Mock requests.get
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "info": {
                "version": "1.0.1"
            }
        }
        mock_get.return_value = mock_response

        # Mock current version
        with mock.patch("hubqueue.system.__version__", "1.0.0"):
            # Check for updates
            update_info = check_for_updates()

            # Verify result
            self.assertEqual(update_info["current_version"], "0.1.0")
            self.assertEqual(update_info["latest_version"], "1.0.1")
            self.assertTrue(update_info["update_available"])
            mock_get.assert_called_once_with("https://pypi.org/pypi/hubqueue/json")

    @mock.patch("hubqueue.system.subprocess.run")
    @mock.patch("hubqueue.system.check_command_availability")
    def test_update_hubqueue(self, mock_check, mock_run):
        """Test updating HubQueue."""
        # Mock check_command_availability
        mock_check.return_value = True

        # Mock subprocess.run
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Update HubQueue
        result = update_hubqueue()

        # Verify result
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "hubqueue"],
            stdout=mock.ANY, stderr=mock.ANY, text=True
        )
