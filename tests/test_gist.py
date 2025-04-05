"""
Tests for the gist module.
"""
import tempfile
import os
from unittest import TestCase, mock

from hubqueue.gist import (
    list_gists, get_gist, create_gist, update_gist, delete_gist,
    star_gist, unstar_gist, is_gist_starred, add_gist_comment,
    delete_gist_comment, fork_gist, download_gist, upload_gist
)


class TestGist(TestCase):
    """Test gist management functions."""

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

    @mock.patch("hubqueue.gist.Github")
    def test_list_gists(self, mock_github):
        """Test listing gists."""
        # Mock GitHub API
        mock_file1 = mock.MagicMock()
        mock_file1.filename = "file1.txt"
        mock_file1.language = "Text"
        mock_file1.size = 100
        mock_file1.raw_url = "https://gist.githubusercontent.com/raw/file1.txt"

        mock_file2 = mock.MagicMock()
        mock_file2.filename = "file2.py"
        mock_file2.language = "Python"
        mock_file2.size = 200
        mock_file2.raw_url = "https://gist.githubusercontent.com/raw/file2.py"

        mock_gist1 = mock.MagicMock()
        mock_gist1.id = "gist1"
        mock_gist1.description = "Test Gist 1"
        mock_gist1.public = True
        mock_gist1.created_at = "2023-01-01T00:00:00Z"
        mock_gist1.updated_at = "2023-01-02T00:00:00Z"
        mock_gist1.html_url = "https://gist.github.com/gist1"
        mock_gist1.files = {"file1.txt": mock_file1}
        mock_gist1.comments = 2

        mock_gist2 = mock.MagicMock()
        mock_gist2.id = "gist2"
        mock_gist2.description = "Test Gist 2"
        mock_gist2.public = False
        mock_gist2.created_at = "2023-01-03T00:00:00Z"
        mock_gist2.updated_at = "2023-01-04T00:00:00Z"
        mock_gist2.html_url = "https://gist.github.com/gist2"
        mock_gist2.files = {"file2.py": mock_file2}
        mock_gist2.comments = 0

        mock_user = mock.MagicMock()
        mock_user.get_gists.return_value = [mock_gist1, mock_gist2]
        mock_user.get_starred_gists.return_value = [mock_gist1]

        mock_github.return_value.get_user.return_value = mock_user

        # List all gists
        gists = list_gists(False, False, "test-token")

        # Verify result
        self.assertEqual(len(gists), 2)

        self.assertEqual(gists[0]["id"], "gist1")
        self.assertEqual(gists[0]["description"], "Test Gist 1")
        self.assertEqual(gists[0]["public"], True)
        self.assertEqual(gists[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(gists[0]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(gists[0]["url"], "https://gist.github.com/gist1")
        self.assertEqual(gists[0]["comments"], 2)
        self.assertEqual(len(gists[0]["files"]), 1)
        self.assertEqual(gists[0]["files"]["file1.txt"]["filename"], "file1.txt")
        self.assertEqual(gists[0]["files"]["file1.txt"]["language"], "Text")
        self.assertEqual(gists[0]["files"]["file1.txt"]["size"], 100)
        self.assertEqual(gists[0]["files"]["file1.txt"]["raw_url"], "https://gist.githubusercontent.com/raw/file1.txt")

        self.assertEqual(gists[1]["id"], "gist2")
        self.assertEqual(gists[1]["public"], False)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_gists.assert_called_once()
        mock_user.get_starred_gists.assert_not_called()

        # Reset mocks
        mock_github.reset_mock()
        mock_user.reset_mock()

        # List public gists
        gists = list_gists(True, False, "test-token")

        # Verify result
        self.assertEqual(len(gists), 1)
        self.assertEqual(gists[0]["id"], "gist1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_gists.assert_called_once()

        # Reset mocks
        mock_github.reset_mock()
        mock_user.reset_mock()

        # List starred gists
        gists = list_gists(False, True, "test-token")

        # Verify result
        self.assertEqual(len(gists), 1)
        self.assertEqual(gists[0]["id"], "gist1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_starred_gists.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_get_gist(self, mock_github):
        """Test getting a gist."""
        # Mock GitHub API
        mock_file = mock.MagicMock()
        mock_file.filename = "file.txt"
        mock_file.language = "Text"
        mock_file.size = 100
        mock_file.raw_url = "https://gist.githubusercontent.com/raw/file.txt"
        mock_file.content = "Test content"

        mock_comment = mock.MagicMock()
        mock_comment.id = 1
        mock_comment.user.login = "test-user"
        mock_comment.body = "Test comment"
        mock_comment.created_at = "2023-01-02T00:00:00Z"
        mock_comment.updated_at = "2023-01-02T00:00:00Z"

        mock_gist = mock.MagicMock()
        mock_gist.id = "gist1"
        mock_gist.description = "Test Gist"
        mock_gist.public = True
        mock_gist.created_at = "2023-01-01T00:00:00Z"
        mock_gist.updated_at = "2023-01-02T00:00:00Z"
        mock_gist.html_url = "https://gist.github.com/gist1"
        mock_gist.files = {"file.txt": mock_file}
        mock_gist.owner.login = "test-user"
        mock_gist.get_comments.return_value = [mock_comment]

        mock_github.return_value.get_gist.return_value = mock_gist

        # Get gist
        gist = get_gist("gist1", "test-token")

        # Verify result
        self.assertEqual(gist["id"], "gist1")
        self.assertEqual(gist["description"], "Test Gist")
        self.assertEqual(gist["public"], True)
        self.assertEqual(gist["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(gist["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(gist["url"], "https://gist.github.com/gist1")
        self.assertEqual(gist["owner"], "test-user")

        # Verify files
        self.assertEqual(len(gist["files"]), 1)
        self.assertEqual(gist["files"]["file.txt"]["filename"], "file.txt")
        self.assertEqual(gist["files"]["file.txt"]["language"], "Text")
        self.assertEqual(gist["files"]["file.txt"]["size"], 100)
        self.assertEqual(gist["files"]["file.txt"]["raw_url"], "https://gist.githubusercontent.com/raw/file.txt")
        self.assertEqual(gist["files"]["file.txt"]["content"], "Test content")

        # Verify comments
        self.assertEqual(len(gist["comments"]), 1)
        self.assertEqual(gist["comments"][0]["id"], 1)
        self.assertEqual(gist["comments"][0]["user"], "test-user")
        self.assertEqual(gist["comments"][0]["body"], "Test comment")
        self.assertEqual(gist["comments"][0]["created_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(gist["comments"][0]["updated_at"], "2023-01-02T00:00:00Z")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.get_comments.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_create_gist(self, mock_github):
        """Test creating a gist."""
        # Mock GitHub API
        mock_file = mock.MagicMock()
        mock_file.filename = "file.txt"
        mock_file.language = "Text"
        mock_file.size = 100
        mock_file.raw_url = "https://gist.githubusercontent.com/raw/file.txt"

        mock_gist = mock.MagicMock()
        mock_gist.id = "gist1"
        mock_gist.description = "Test Gist"
        mock_gist.public = True
        mock_gist.created_at = "2023-01-01T00:00:00Z"
        mock_gist.updated_at = "2023-01-01T00:00:00Z"
        mock_gist.html_url = "https://gist.github.com/gist1"
        mock_gist.files = {"file.txt": mock_file}

        mock_user = mock.MagicMock()
        mock_user.create_gist.return_value = mock_gist

        mock_github.return_value.get_user.return_value = mock_user

        # Create gist
        files = {"file.txt": "Test content"}
        gist = create_gist(files, "Test Gist", True, "test-token")

        # Verify result
        self.assertEqual(gist["id"], "gist1")
        self.assertEqual(gist["description"], "Test Gist")
        self.assertEqual(gist["public"], True)
        self.assertEqual(gist["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(gist["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(gist["url"], "https://gist.github.com/gist1")

        # Verify files
        self.assertEqual(len(gist["files"]), 1)
        self.assertEqual(gist["files"]["file.txt"]["filename"], "file.txt")
        self.assertEqual(gist["files"]["file.txt"]["language"], "Text")
        self.assertEqual(gist["files"]["file.txt"]["size"], 100)
        self.assertEqual(gist["files"]["file.txt"]["raw_url"], "https://gist.githubusercontent.com/raw/file.txt")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.create_gist.assert_called_once_with(True, files, "Test Gist")

    @mock.patch("hubqueue.gist.Github")
    def test_update_gist(self, mock_github):
        """Test updating a gist."""
        # Mock GitHub API
        mock_file = mock.MagicMock()
        mock_file.filename = "file.txt"
        mock_file.language = "Text"
        mock_file.size = 100
        mock_file.raw_url = "https://gist.githubusercontent.com/raw/file.txt"

        mock_gist = mock.MagicMock()
        mock_gist.id = "gist1"
        mock_gist.description = "Updated Gist"
        mock_gist.public = True
        mock_gist.created_at = "2023-01-01T00:00:00Z"
        mock_gist.updated_at = "2023-01-02T00:00:00Z"
        mock_gist.html_url = "https://gist.github.com/gist1"
        mock_gist.files = {"file.txt": mock_file}

        mock_github.return_value.get_gist.return_value = mock_gist

        # Update gist
        files = {"file.txt": "Updated content"}
        gist = update_gist("gist1", files, "Updated Gist", "test-token")

        # Verify result
        self.assertEqual(gist["id"], "gist1")
        self.assertEqual(gist["description"], "Updated Gist")
        self.assertEqual(gist["public"], True)
        self.assertEqual(gist["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(gist["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(gist["url"], "https://gist.github.com/gist1")

        # Verify files
        self.assertEqual(len(gist["files"]), 1)
        self.assertEqual(gist["files"]["file.txt"]["filename"], "file.txt")
        self.assertEqual(gist["files"]["file.txt"]["language"], "Text")
        self.assertEqual(gist["files"]["file.txt"]["size"], 100)
        self.assertEqual(gist["files"]["file.txt"]["raw_url"], "https://gist.githubusercontent.com/raw/file.txt")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.edit.assert_called_once_with(description="Updated Gist", files=files)

    @mock.patch("hubqueue.gist.Github")
    def test_delete_gist(self, mock_github):
        """Test deleting a gist."""
        # Mock GitHub API
        mock_gist = mock.MagicMock()

        mock_github.return_value.get_gist.return_value = mock_gist

        # Delete gist
        result = delete_gist("gist1", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.delete.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_star_gist(self, mock_github):
        """Test starring a gist."""
        # Mock GitHub API
        mock_gist = mock.MagicMock()

        mock_github.return_value.get_gist.return_value = mock_gist

        # Star gist
        result = star_gist("gist1", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.set_starred.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_unstar_gist(self, mock_github):
        """Test unstarring a gist."""
        # Mock GitHub API
        mock_gist = mock.MagicMock()

        mock_github.return_value.get_gist.return_value = mock_gist

        # Unstar gist
        result = unstar_gist("gist1", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.reset_starred.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_is_gist_starred(self, mock_github):
        """Test checking if a gist is starred."""
        # Mock GitHub API
        mock_gist = mock.MagicMock()
        mock_gist.is_starred.return_value = True

        mock_github.return_value.get_gist.return_value = mock_gist

        # Check if gist is starred
        result = is_gist_starred("gist1", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.is_starred.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_add_gist_comment(self, mock_github):
        """Test adding a comment to a gist."""
        # Mock GitHub API
        mock_comment = mock.MagicMock()
        mock_comment.id = 1
        mock_comment.user.login = "test-user"
        mock_comment.body = "Test comment"
        mock_comment.created_at = "2023-01-01T00:00:00Z"
        mock_comment.updated_at = "2023-01-01T00:00:00Z"

        mock_gist = mock.MagicMock()
        mock_gist.create_comment.return_value = mock_comment

        mock_github.return_value.get_gist.return_value = mock_gist

        # Add comment
        comment = add_gist_comment("gist1", "Test comment", "test-token")

        # Verify result
        self.assertEqual(comment["id"], 1)
        self.assertEqual(comment["user"], "test-user")
        self.assertEqual(comment["body"], "Test comment")
        self.assertEqual(comment["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(comment["updated_at"], "2023-01-01T00:00:00Z")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.create_comment.assert_called_once_with("Test comment")

    @mock.patch("hubqueue.gist.Github")
    def test_delete_gist_comment(self, mock_github):
        """Test deleting a comment from a gist."""
        # Mock GitHub API
        mock_comment = mock.MagicMock()

        mock_gist = mock.MagicMock()
        mock_gist.get_comment.return_value = mock_comment

        mock_github.return_value.get_gist.return_value = mock_gist

        # Delete comment
        result = delete_gist_comment("gist1", 1, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.get_comment.assert_called_once_with(1)
        mock_comment.delete.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_fork_gist(self, mock_github):
        """Test forking a gist."""
        # Mock GitHub API
        mock_file = mock.MagicMock()
        mock_file.filename = "file.txt"
        mock_file.language = "Text"
        mock_file.size = 100
        mock_file.raw_url = "https://gist.githubusercontent.com/raw/file.txt"

        mock_forked_gist = mock.MagicMock()
        mock_forked_gist.id = "gist2"
        mock_forked_gist.description = "Test Gist"
        mock_forked_gist.public = True
        mock_forked_gist.created_at = "2023-01-02T00:00:00Z"
        mock_forked_gist.updated_at = "2023-01-02T00:00:00Z"
        mock_forked_gist.html_url = "https://gist.github.com/gist2"
        mock_forked_gist.files = {"file.txt": mock_file}

        mock_gist = mock.MagicMock()
        mock_gist.create_fork.return_value = mock_forked_gist

        mock_github.return_value.get_gist.return_value = mock_gist

        # Fork gist
        forked_gist = fork_gist("gist1", "test-token")

        # Verify result
        self.assertEqual(forked_gist["id"], "gist2")
        self.assertEqual(forked_gist["description"], "Test Gist")
        self.assertEqual(forked_gist["public"], True)
        self.assertEqual(forked_gist["created_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(forked_gist["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(forked_gist["url"], "https://gist.github.com/gist2")

        # Verify files
        self.assertEqual(len(forked_gist["files"]), 1)
        self.assertEqual(forked_gist["files"]["file.txt"]["filename"], "file.txt")
        self.assertEqual(forked_gist["files"]["file.txt"]["language"], "Text")
        self.assertEqual(forked_gist["files"]["file.txt"]["size"], 100)
        self.assertEqual(forked_gist["files"]["file.txt"]["raw_url"], "https://gist.githubusercontent.com/raw/file.txt")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")
        mock_gist.create_fork.assert_called_once()

    @mock.patch("hubqueue.gist.Github")
    def test_download_gist(self, mock_github):
        """Test downloading a gist."""
        # Create test directory
        os.makedirs(self.temp_dir, exist_ok=True)

        # Mock GitHub API
        mock_file = mock.MagicMock()
        mock_file.filename = "file.txt"
        mock_file.content = "Test content"

        mock_gist = mock.MagicMock()
        mock_gist.files = {"file.txt": mock_file}

        mock_github.return_value.get_gist.return_value = mock_gist

        # Download gist
        downloaded_files = download_gist("gist1", self.temp_dir, "test-token")

        # Verify result
        self.assertEqual(len(downloaded_files), 1)
        self.assertEqual(os.path.basename(downloaded_files[0]), "file.txt")

        # Verify file content
        with open(downloaded_files[0], "r") as f:
            content = f.read()
            self.assertEqual(content, "Test content")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_gist.assert_called_once_with("gist1")

    @mock.patch("hubqueue.gist.create_gist")
    def test_upload_gist(self, mock_create_gist):
        """Test uploading files to a gist."""
        # Create test files
        test_file = os.path.join(self.temp_dir, "file.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        # Mock create_gist
        mock_create_gist.return_value = {
            "id": "gist1",
            "url": "https://gist.github.com/gist1",
            "files": {"file.txt": {"filename": "file.txt"}}
        }

        # Upload gist
        gist = upload_gist([test_file], "Test Gist", True, "test-token")

        # Verify result
        self.assertEqual(gist["id"], "gist1")
        self.assertEqual(gist["url"], "https://gist.github.com/gist1")
        self.assertEqual(len(gist["files"]), 1)
        self.assertEqual(gist["files"]["file.txt"]["filename"], "file.txt")

        # Verify API calls
        mock_create_gist.assert_called_once()
        args = mock_create_gist.call_args[0]
        # Check that create_gist was called with the right arguments
        self.assertEqual(len(args), 4)  # files, description, public, token
        self.assertEqual(args[1], "Test Gist")
        self.assertEqual(args[2], True)
        self.assertEqual(args[3], "test-token")
        self.assertEqual(len(args[0]), 1)
        self.assertEqual(args[0]["file.txt"], "Test content")
