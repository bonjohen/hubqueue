"""
Tests for the utils module.
"""
import os
import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.utils import get_config_dir, save_config, load_config, get_github_token


class TestUtils(TestCase):
    """Test utility functions."""

    def test_get_config_dir(self):
        """Test that the config directory is created."""
        with mock.patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(tempfile.gettempdir())
            config_dir = get_config_dir()
            self.assertTrue(config_dir.exists())
            self.assertEqual(config_dir, Path(tempfile.gettempdir()) / ".hubqueue")

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        test_config = {"github_token": "test-token", "default_repo": "owner/repo"}
        
        with mock.patch("hubqueue.utils.get_config_dir") as mock_get_config_dir:
            temp_dir = Path(tempfile.mkdtemp())
            mock_get_config_dir.return_value = temp_dir
            
            save_config(test_config)
            loaded_config = load_config()
            
            self.assertEqual(loaded_config, test_config)
            
            # Clean up
            (temp_dir / "config.json").unlink()
            temp_dir.rmdir()

    def test_get_github_token_from_env(self):
        """Test getting GitHub token from environment variable."""
        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"}):
            token = get_github_token()
            self.assertEqual(token, "env-token")

    def test_get_github_token_from_config(self):
        """Test getting GitHub token from config file."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("hubqueue.utils.load_config") as mock_load_config:
                mock_load_config.return_value = {"github_token": "config-token"}
                token = get_github_token()
                self.assertEqual(token, "config-token")
