"""
Tests for the release module.
"""
import tempfile
import subprocess
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.release import (
    update_version, create_tag, push_tag,
    generate_release_notes, create_github_release,
    upload_release_asset
)


class TestRelease(TestCase):
    """Test release management functions."""

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

    def test_update_version(self):
        """Test updating version identifiers in files."""
        # Create test files
        init_file = Path(self.temp_dir) / "__init__.py"
        with open(init_file, "w") as f:
            f.write('__version__ = "1.0.0"')
        
        setup_file = Path(self.temp_dir) / "setup.py"
        with open(setup_file, "w") as f:
            f.write('setup(\n    version="1.0.0",\n)')
        
        # Update version
        result = update_version(self.temp_dir, "1.1.0")
        
        # Verify result
        self.assertEqual(result["old_version"], "1.0.0")
        self.assertEqual(result["new_version"], "1.1.0")
        self.assertEqual(len(result["updated_files"]), 2)
        
        # Verify file contents
        with open(init_file, "r") as f:
            content = f.read()
            self.assertIn('__version__ = "1.1.0"', content)
        
        with open(setup_file, "r") as f:
            content = f.read()
            self.assertIn('version="1.1.0"', content)

    def test_update_version_auto_increment(self):
        """Test auto-incrementing version."""
        # Create test file
        init_file = Path(self.temp_dir) / "__init__.py"
        with open(init_file, "w") as f:
            f.write('__version__ = "1.0.0"')
        
        # Update version without specifying new version
        result = update_version(self.temp_dir)
        
        # Verify result
        self.assertEqual(result["old_version"], "1.0.0")
        self.assertEqual(result["new_version"], "1.0.1")
        
        # Verify file contents
        with open(init_file, "r") as f:
            content = f.read()
            self.assertIn('__version__ = "1.0.1"', content)

    def test_update_version_custom_pattern(self):
        """Test updating version with custom pattern."""
        # Create test file
        version_file = Path(self.temp_dir) / "version.txt"
        with open(version_file, "w") as f:
            f.write('Version: v1.0')
        
        # Update version with custom pattern
        result = update_version(self.temp_dir, "v2.0", r'v\d+\.\d+')
        
        # Verify result
        self.assertEqual(result["old_version"], "v1.0")
        self.assertEqual(result["new_version"], "v2.0")
        
        # Verify file contents
        with open(version_file, "r") as f:
            content = f.read()
            self.assertIn('Version: v2.0', content)

    @mock.patch("subprocess.run")
    def test_create_tag(self, mock_run):
        """Test creating a Git tag."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        
        # Create tag
        tag_name = create_tag("v1.0.0", "Release v1.0.0", self.temp_dir, False)
        
        # Verify result
        self.assertEqual(tag_name, "v1.0.0")
        
        # Verify subprocess call
        mock_run.assert_called_once_with(
            ["git", "tag", "-a", "v1.0.0", "-m", "Release v1.0.0"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("subprocess.run")
    def test_create_signed_tag(self, mock_run):
        """Test creating a signed Git tag."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        
        # Create signed tag
        tag_name = create_tag("v1.0.0", "Release v1.0.0", self.temp_dir, True)
        
        # Verify result
        self.assertEqual(tag_name, "v1.0.0")
        
        # Verify subprocess call
        mock_run.assert_called_once_with(
            ["git", "tag", "-s", "-a", "v1.0.0", "-m", "Release v1.0.0"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("subprocess.run")
    def test_push_tag(self, mock_run):
        """Test pushing a Git tag."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        
        # Push tag
        result = push_tag("v1.0.0", "origin", self.temp_dir)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify subprocess call
        mock_run.assert_called_once_with(
            ["git", "push", "origin", "v1.0.0"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("subprocess.run")
    def test_generate_release_notes(self, mock_run):
        """Test generating release notes."""
        # Mock subprocess.run
        mock_run.side_effect = [
            # git describe
            subprocess.CompletedProcess(args=[], returncode=0, stdout="v0.9.0", stderr=""),
            # git log
            subprocess.CompletedProcess(
                args=[], 
                returncode=0, 
                stdout="abc123 feat: Add new feature (User1)\ndef456 fix: Fix bug (User2)\nghi789 docs: Update docs (User3)",
                stderr=""
            )
        ]
        
        # Generate release notes
        notes = generate_release_notes("v1.0.0", None, self.temp_dir)
        
        # Verify result
        self.assertIn("# Release v1.0.0", notes)
        self.assertIn("## Features", notes)
        self.assertIn("* abc123 feat: Add new feature (User1)", notes)
        self.assertIn("## Bug Fixes", notes)
        self.assertIn("* def456 fix: Fix bug (User2)", notes)
        self.assertIn("## Documentation", notes)
        self.assertIn("* ghi789 docs: Update docs (User3)", notes)

    @mock.patch("hubqueue.release.Github")
    def test_create_github_release(self, mock_github):
        """Test creating a GitHub release."""
        # Mock GitHub API
        mock_release = mock.MagicMock()
        mock_release.id = 12345
        mock_release.tag_name = "v1.0.0"
        mock_release.title = "v1.0.0"
        mock_release.body = "Release notes"
        mock_release.draft = False
        mock_release.prerelease = False
        mock_release.created_at = "2023-01-01T00:00:00Z"
        mock_release.html_url = "https://github.com/test-user/test-repo/releases/tag/v1.0.0"
        
        mock_repo = mock.MagicMock()
        mock_repo.create_git_release.return_value = mock_release
        
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Create GitHub release
        release = create_github_release(
            "test-user/test-repo",
            "v1.0.0",
            "v1.0.0",
            "Release notes",
            False,
            False,
            "test-token"
        )
        
        # Verify result
        self.assertEqual(release["id"], 12345)
        self.assertEqual(release["tag_name"], "v1.0.0")
        self.assertEqual(release["name"], "v1.0.0")
        self.assertEqual(release["body"], "Release notes")
        self.assertEqual(release["draft"], False)
        self.assertEqual(release["prerelease"], False)
        self.assertEqual(release["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(release["html_url"], "https://github.com/test-user/test-repo/releases/tag/v1.0.0")
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.create_git_release.assert_called_once_with(
            tag="v1.0.0",
            name="v1.0.0",
            message="Release notes",
            draft=False,
            prerelease=False
        )

    @mock.patch("hubqueue.release.Path.exists")
    @mock.patch("hubqueue.release.Github")
    def test_upload_release_asset(self, mock_github, mock_exists):
        """Test uploading a release asset."""
        # Mock Path.exists
        mock_exists.return_value = True
        
        # Mock GitHub API
        mock_asset = mock.MagicMock()
        mock_asset.id = 67890
        mock_asset.name = "test-asset.zip"
        mock_asset.label = "test-asset.zip"
        mock_asset.content_type = "application/zip"
        mock_asset.size = 1024
        mock_asset.download_count = 0
        mock_asset.browser_download_url = "https://github.com/test-user/test-repo/releases/download/v1.0.0/test-asset.zip"
        
        mock_release = mock.MagicMock()
        mock_release.upload_asset.return_value = mock_asset
        
        mock_repo = mock.MagicMock()
        mock_repo.get_release.return_value = mock_release
        
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Upload release asset
        asset = upload_release_asset(
            "test-user/test-repo",
            12345,
            "test-asset.zip",
            None,
            "test-token"
        )
        
        # Verify result
        self.assertEqual(asset["id"], 67890)
        self.assertEqual(asset["name"], "test-asset.zip")
        self.assertEqual(asset["label"], "test-asset.zip")
        self.assertEqual(asset["content_type"], "application/zip")
        self.assertEqual(asset["size"], 1024)
        self.assertEqual(asset["download_count"], 0)
        self.assertEqual(asset["browser_download_url"], "https://github.com/test-user/test-repo/releases/download/v1.0.0/test-asset.zip")
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_release.assert_called_once_with(12345)
        mock_release.upload_asset.assert_called_once_with(
            path="test-asset.zip",
            label="test-asset.zip",
            content_type=None
        )
