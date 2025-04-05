"""
Tests for the repository module.
"""
import os
import tempfile
import subprocess
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.repository import (
    create_repository, clone_repository, init_repository,
    create_project_directories, generate_gitignore, generate_readme,
    generate_license, create_branch, stage_and_commit, push_commits,
    create_pull_request, fork_repository, manage_collaborators
)


class TestRepository(TestCase):
    """Test repository management functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patcher = mock.patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()

        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @mock.patch("hubqueue.repository.Github")
    def test_create_repository(self, mock_github):
        """Test creating a repository."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "test-user/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.private = False
        mock_repo.html_url = "https://github.com/test-user/test-repo"
        mock_repo.clone_url = "https://github.com/test-user/test-repo.git"
        mock_repo.ssh_url = "git@github.com:test-user/test-repo.git"

        mock_user = mock.MagicMock()
        mock_user.create_repo.return_value = mock_repo
        mock_github.return_value.get_user.return_value = mock_user

        # Create repository
        repo_info = create_repository("test-repo", "Test repository", False, "test-token")

        # Verify result
        self.assertEqual(repo_info["name"], "test-repo")
        self.assertEqual(repo_info["full_name"], "test-user/test-repo")
        self.assertEqual(repo_info["description"], "Test repository")
        self.assertEqual(repo_info["private"], False)
        self.assertEqual(repo_info["html_url"], "https://github.com/test-user/test-repo")
        self.assertEqual(repo_info["clone_url"], "https://github.com/test-user/test-repo.git")
        self.assertEqual(repo_info["ssh_url"], "git@github.com:test-user/test-repo.git")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.create_repo.assert_called_once_with(
            name="test-repo",
            description="Test repository",
            private=False,
            auto_init=True
        )

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_clone_repository(self, mock_run):
        """Test cloning a repository."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        # Clone repository
        repo_path = clone_repository("https://github.com/test-user/test-repo.git", "test-dir", "test-token")

        # Verify result
        self.assertEqual(repo_path, str(Path("test-dir").absolute()))

        # Verify subprocess call
        mock_run.assert_called_once_with(
            ["git", "clone", "https://test-token@github.com/test-user/test-repo.git", "test-dir"],
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_init_repository(self, mock_run):
        """Test initializing a repository."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        # Initialize repository
        result = init_repository(self.temp_dir)

        # Verify result
        self.assertTrue(result)

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(
            ["git", "init"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "checkout", "-b", "main"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    def test_create_project_directories(self):
        """Test creating project directories."""
        # Create project directories
        dirs = ["src", "tests", "docs"]
        created_dirs = create_project_directories(self.temp_dir, dirs)

        # Verify result
        self.assertEqual(len(created_dirs), 3)
        for dir_name in dirs:
            dir_path = Path(self.temp_dir) / dir_name
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_generate_gitignore(self, mock_run):
        """Test generating a .gitignore file."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="# Python gitignore template", stderr=""
        )

        # Generate .gitignore
        gitignore_path = generate_gitignore(self.temp_dir, "Python")

        # Verify result
        self.assertEqual(gitignore_path, str(Path(self.temp_dir) / ".gitignore"))

        # Verify subprocess call
        mock_run.assert_called_once_with(
            ["curl", "-s", "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"],
            check=True,
            capture_output=True,
            text=True
        )

        # Verify file content
        with open(Path(self.temp_dir) / ".gitignore", "r") as f:
            content = f.read()
            self.assertEqual(content, "# Python gitignore template")

    def test_generate_readme(self):
        """Test generating a README.md file."""
        # Generate README.md
        readme_path = generate_readme(self.temp_dir, "Test Project", "A test project")

        # Verify result
        self.assertEqual(readme_path, str(Path(self.temp_dir) / "README.md"))

        # Verify file content
        with open(Path(self.temp_dir) / "README.md", "r") as f:
            content = f.read()
            self.assertTrue("# Test Project" in content)
            self.assertTrue("A test project" in content)
            self.assertTrue("## Installation" in content)
            self.assertTrue("## Usage" in content)
            self.assertTrue("## License" in content)

    def test_generate_license(self):
        """Test generating a LICENSE file."""
        # Generate LICENSE
        license_path = generate_license(self.temp_dir, "MIT", "Test User")

        # Verify result
        self.assertEqual(license_path, str(Path(self.temp_dir) / "LICENSE"))

        # Verify file content
        with open(Path(self.temp_dir) / "LICENSE", "r") as f:
            content = f.read()
            self.assertTrue("MIT License" in content)
            self.assertTrue("Test User" in content)
            self.assertTrue("Permission is hereby granted" in content)

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_create_branch(self, mock_run):
        """Test creating a branch."""
        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        # Create branch
        branch_name = create_branch("feature-branch", "main", self.temp_dir)

        # Verify result
        self.assertEqual(branch_name, "feature-branch")

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(
            ["git", "checkout", "main"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "pull", "--ff-only"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "checkout", "-b", "feature-branch"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_stage_and_commit(self, mock_run):
        """Test staging and committing changes."""
        # Mock subprocess.run
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git add
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123", stderr="")  # git rev-parse
        ]

        # Stage and commit
        commit_hash = stage_and_commit("Test commit", self.temp_dir)

        # Verify result
        self.assertEqual(commit_hash, "abc123")

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(
            ["git", "add", "."],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "commit", "-m", "Test commit"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "rev-parse", "HEAD"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("hubqueue.repository.subprocess.run")
    def test_push_commits(self, mock_run):
        """Test pushing commits."""
        # Mock subprocess.run
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="feature-branch", stderr=""),  # git rev-parse
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")  # git push
        ]

        # Push commits
        result = push_commits("origin", None, self.temp_dir)

        # Verify result
        self.assertTrue(result)

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "push", "-u", "origin", "feature-branch"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("hubqueue.repository.subprocess.run")
    @mock.patch("hubqueue.repository.Github")
    def test_create_pull_request(self, mock_github, mock_run):
        """Test creating a pull request."""
        # Mock subprocess.run
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="feature-branch", stderr=""),  # git rev-parse
            subprocess.CompletedProcess(args=[], returncode=0, stdout="https://github.com/test-user/test-repo.git", stderr="")  # git remote
        ]

        # Mock GitHub API
        mock_pr = mock.MagicMock()
        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/test-user/test-repo/pull/123"
        mock_pr.state = "open"

        mock_repo = mock.MagicMock()
        mock_repo.create_pull.return_value = mock_pr

        mock_github.return_value.get_repo.return_value = mock_repo

        # Create pull request
        pr_info = create_pull_request("Test PR", "Test description", "main", "feature-branch", "test-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(pr_info["number"], 123)
        self.assertEqual(pr_info["title"], "Test PR")
        self.assertEqual(pr_info["html_url"], "https://github.com/test-user/test-repo/pull/123")
        self.assertEqual(pr_info["state"], "open")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.create_pull.assert_called_once_with(
            title="Test PR",
            body="Test description",
            base="main",
            head="feature-branch"
        )

    @mock.patch("hubqueue.repository.Github")
    def test_fork_repository(self, mock_github):
        """Test forking a repository."""
        # Mock GitHub API
        mock_fork = mock.MagicMock()
        mock_fork.name = "test-repo"
        mock_fork.full_name = "test-user/test-repo"
        mock_fork.description = "Test repository"
        mock_fork.html_url = "https://github.com/test-user/test-repo"
        mock_fork.clone_url = "https://github.com/test-user/test-repo.git"
        mock_fork.ssh_url = "git@github.com:test-user/test-repo.git"

        mock_repo = mock.MagicMock()
        mock_repo.create_fork.return_value = mock_fork

        mock_github.return_value.get_repo.return_value = mock_repo

        # Fork repository
        fork_info = fork_repository("original-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(fork_info["name"], "test-repo")
        self.assertEqual(fork_info["full_name"], "test-user/test-repo")
        self.assertEqual(fork_info["description"], "Test repository")
        self.assertEqual(fork_info["html_url"], "https://github.com/test-user/test-repo")
        self.assertEqual(fork_info["clone_url"], "https://github.com/test-user/test-repo.git")
        self.assertEqual(fork_info["ssh_url"], "git@github.com:test-user/test-repo.git")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("original-user/test-repo")
        mock_repo.create_fork.assert_called_once()

    @mock.patch("hubqueue.repository.Github")
    def test_manage_collaborators_add(self, mock_github):
        """Test adding a collaborator."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # Add collaborator
        result = manage_collaborators("test-user/test-repo", "collaborator", "push", True, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.add_to_collaborators.assert_called_once_with("collaborator", "push")
        mock_repo.remove_from_collaborators.assert_not_called()

    @mock.patch("hubqueue.repository.Github")
    def test_manage_collaborators_remove(self, mock_github):
        """Test removing a collaborator."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # Remove collaborator
        result = manage_collaborators("test-user/test-repo", "collaborator", "push", False, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.add_to_collaborators.assert_not_called()
        mock_repo.remove_from_collaborators.assert_called_once_with("collaborator")
