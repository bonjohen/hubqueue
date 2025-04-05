"""
Tests for the auth module.
"""
import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.auth import (
    get_github_token, validate_token, save_token,
    clear_token, get_user_info
)


class TestAuth(TestCase):
    """Test authentication functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary config directory
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir_patcher = mock.patch("hubqueue.utils.get_config_dir")
        self.mock_get_config_dir = self.config_dir_patcher.start()
        self.mock_get_config_dir.return_value = Path(self.temp_dir)

        # Mock environment variables
        self.env_patcher = mock.patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.config_dir_patcher.stop()
        self.env_patcher.stop()

        # Clean up temporary directory
        config_file = Path(self.temp_dir) / "config.json"
        if config_file.exists():
            config_file.unlink()
        Path(self.temp_dir).rmdir()

    def test_get_github_token_from_env(self):
        """Test getting GitHub token from environment variable."""
        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
            token = get_github_token()
            self.assertEqual(token, "test-token")

    def test_get_github_token_from_config(self):
        """Test getting GitHub token from config file."""
        save_token("config-token")
        with mock.patch.dict(os.environ, {}, clear=True):
            token = get_github_token()
            self.assertEqual(token, "config-token")

    def test_save_and_clear_token(self):
        """Test saving and clearing GitHub token."""
        # Save token
        save_token("test-token")
        token = get_github_token()
        self.assertEqual(token, "test-token")

        # Clear token
        result = clear_token()
        self.assertTrue(result)
        token = get_github_token()
        self.assertIsNone(token)

        # Clear when no token exists
        result = clear_token()
        self.assertFalse(result)

    @mock.patch("hubqueue.auth.Github")
    def test_validate_token_valid(self, mock_github):
        """Test validating a valid GitHub token."""
        # Mock GitHub API
        mock_user = mock.MagicMock()
        mock_user.login = "test-user"
        mock_github.return_value.get_user.return_value = mock_user

        result = validate_token("valid-token")
        self.assertTrue(result)
        mock_github.assert_called_once_with("valid-token")

    @mock.patch("hubqueue.auth.Github")
    def test_validate_token_invalid(self, mock_github):
        """Test validating an invalid GitHub token."""
        # Mock GitHub API to raise exception
        from github.GithubException import BadCredentialsException
        mock_github.return_value.get_user.side_effect = BadCredentialsException(
            status=401, data={"message": "Bad credentials"}, headers={}
        )

        result = validate_token("invalid-token")
        self.assertFalse(result)

    def test_validate_token_none(self):
        """Test validating None token."""
        result = validate_token(None)
        self.assertFalse(result)

    @mock.patch("hubqueue.auth.Github")
    def test_get_user_info(self, mock_github):
        """Test getting user information."""
        # Mock GitHub API
        mock_user = mock.MagicMock()
        mock_user.login = "test-user"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.avatar_url = "https://example.com/avatar.png"
        mock_user.html_url = "https://github.com/test-user"
        mock_user.public_repos = 10
        mock_user.total_private_repos = 5
        mock_github.return_value.get_user.return_value = mock_user

        user_info = get_user_info("test-token")
        self.assertEqual(user_info["login"], "test-user")
        self.assertEqual(user_info["name"], "Test User")
        self.assertEqual(user_info["email"], "test@example.com")
        self.assertEqual(user_info["avatar_url"], "https://example.com/avatar.png")
        self.assertEqual(user_info["html_url"], "https://github.com/test-user")
        self.assertEqual(user_info["public_repos"], 10)
        self.assertEqual(user_info["private_repos"], 5)

    @mock.patch("hubqueue.auth.Github")
    def test_get_user_info_error(self, mock_github):
        """Test getting user information with error."""
        # Mock GitHub API to raise exception
        mock_github.return_value.get_user.side_effect = Exception("API error")

        user_info = get_user_info("test-token")
        self.assertIsNone(user_info)
