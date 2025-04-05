"""
Tests for the config module.
"""
import os
import tempfile
import subprocess
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.config import (
    get_default_editor, get_preference, set_preference,
    list_preferences, get_editor, edit_file, 
    get_default_repo, set_default_repo
)


class TestConfig(TestCase):
    """Test configuration functions."""

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

    def test_get_default_editor_from_env(self):
        """Test getting default editor from environment variable."""
        with mock.patch.dict(os.environ, {"HUBQUEUE_EDITOR": "test-editor"}):
            editor = get_default_editor()
            self.assertEqual(editor, "test-editor")
        
        with mock.patch.dict(os.environ, {"EDITOR": "test-editor"}):
            editor = get_default_editor()
            self.assertEqual(editor, "test-editor")
        
        with mock.patch.dict(os.environ, {"VISUAL": "test-editor"}):
            editor = get_default_editor()
            self.assertEqual(editor, "test-editor")

    @mock.patch("hubqueue.config.os.name", "nt")
    def test_get_default_editor_windows(self):
        """Test getting default editor on Windows."""
        with mock.patch.dict(os.environ, {}, clear=True):
            editor = get_default_editor()
            self.assertEqual(editor, "notepad.exe")

    @mock.patch("hubqueue.config.os.name", "posix")
    @mock.patch("hubqueue.config.shutil.which")
    def test_get_default_editor_unix(self, mock_which):
        """Test getting default editor on Unix-like systems."""
        # Mock shutil.which to return the first editor
        mock_which.side_effect = lambda cmd: cmd == "vim"
        
        with mock.patch.dict(os.environ, {}, clear=True):
            editor = get_default_editor()
            self.assertEqual(editor, "vim")
        
        # Mock shutil.which to return no editors
        mock_which.side_effect = lambda cmd: None
        
        with mock.patch.dict(os.environ, {}, clear=True):
            editor = get_default_editor()
            self.assertEqual(editor, "nano")

    def test_get_set_preference(self):
        """Test getting and setting preferences."""
        # Test with no preferences set
        value = get_preference("test_key")
        self.assertIsNone(value)
        
        # Test with default value
        value = get_preference("test_key", "default")
        self.assertEqual(value, "default")
        
        # Set a preference
        result = set_preference("test_key", "test_value")
        self.assertTrue(result)
        
        # Get the preference
        value = get_preference("test_key")
        self.assertEqual(value, "test_value")

    def test_list_preferences(self):
        """Test listing preferences."""
        # Test with no preferences set
        prefs = list_preferences()
        self.assertEqual(prefs, {})
        
        # Set some preferences
        set_preference("key1", "value1")
        set_preference("key2", "value2")
        
        # List preferences
        prefs = list_preferences()
        self.assertEqual(prefs, {"key1": "value1", "key2": "value2"})

    def test_get_editor(self):
        """Test getting editor."""
        # Test with no editor set
        with mock.patch("hubqueue.config.get_default_editor") as mock_get_default:
            mock_get_default.return_value = "default-editor"
            editor = get_editor()
            self.assertEqual(editor, "default-editor")
        
        # Set editor preference
        set_preference("editor", "custom-editor")
        
        # Get editor
        editor = get_editor()
        self.assertEqual(editor, "custom-editor")

    @mock.patch("hubqueue.config.subprocess.run")
    def test_edit_file_success(self, mock_run):
        """Test editing a file successfully."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        
        # Set editor preference
        set_preference("editor", "test-editor")
        
        # Edit file
        result = edit_file("test-file.txt")
        self.assertTrue(result)
        mock_run.assert_called_once_with(["test-editor", "test-file.txt"], check=True)

    @mock.patch("hubqueue.config.subprocess.run")
    def test_edit_file_error(self, mock_run):
        """Test editing a file with error."""
        # Mock subprocess.run to raise exception
        mock_run.side_effect = subprocess.SubprocessError("Command failed")
        
        # Set editor preference
        set_preference("editor", "test-editor")
        
        # Edit file
        result = edit_file("test-file.txt")
        self.assertFalse(result)

    def test_get_set_default_repo(self):
        """Test getting and setting default repository."""
        # Test with no default repo set
        repo = get_default_repo()
        self.assertIsNone(repo)
        
        # Set default repo
        result = set_default_repo("owner/repo")
        self.assertTrue(result)
        
        # Get default repo
        repo = get_default_repo()
        self.assertEqual(repo, "owner/repo")
