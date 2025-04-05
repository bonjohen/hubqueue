"""
Tests for the issues module.
"""
import tempfile
import subprocess
from pathlib import Path
from unittest import TestCase, mock

from hubqueue.issues import (
    list_issues, create_issue, list_pull_requests, checkout_pull_request,
    get_issue, get_pull_request
)


class TestIssues(TestCase):
    """Test issue and pull request management functions."""

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

    @mock.patch("hubqueue.issues.Github")
    def test_list_issues(self, mock_github):
        """Test listing issues."""
        # Mock GitHub API
        mock_label1 = mock.MagicMock()
        mock_label1.name = "bug"
        mock_label2 = mock.MagicMock()
        mock_label2.name = "enhancement"

        mock_assignee1 = mock.MagicMock()
        mock_assignee1.login = "assignee1"
        mock_assignee2 = mock.MagicMock()
        mock_assignee2.login = "assignee2"

        mock_issue1 = mock.MagicMock()
        mock_issue1.number = 1
        mock_issue1.title = "Test Issue 1"
        mock_issue1.state = "open"
        mock_issue1.created_at = "2023-01-01T00:00:00Z"
        mock_issue1.updated_at = "2023-01-02T00:00:00Z"
        mock_issue1.html_url = "https://github.com/test-user/test-repo/issues/1"
        mock_issue1.body = "Test issue body"
        mock_issue1.user.login = "test-user"
        mock_issue1.labels = [mock_label1, mock_label2]
        mock_issue1.assignees = [mock_assignee1, mock_assignee2]
        mock_issue1.comments = 2
        mock_issue1.pull_request = None

        mock_issue2 = mock.MagicMock()
        mock_issue2.number = 2
        mock_issue2.title = "Test Issue 2"
        mock_issue2.state = "open"
        mock_issue2.created_at = "2023-01-03T00:00:00Z"
        mock_issue2.updated_at = "2023-01-04T00:00:00Z"
        mock_issue2.html_url = "https://github.com/test-user/test-repo/issues/2"
        mock_issue2.body = "Another test issue body"
        mock_issue2.user.login = "test-user"
        mock_issue2.labels = []
        mock_issue2.assignees = []
        mock_issue2.comments = 0
        mock_issue2.pull_request = None

        # This is a pull request, should be filtered out
        mock_pr = mock.MagicMock()
        mock_pr.number = 3
        mock_pr.title = "Test PR"
        mock_pr.pull_request = mock.MagicMock()

        mock_issues = [mock_issue1, mock_issue2, mock_pr]

        mock_repo = mock.MagicMock()
        mock_repo.get_issues.return_value = mock_issues

        mock_github.return_value.get_repo.return_value = mock_repo

        # List issues
        issues = list_issues("test-user/test-repo", "open", None, None, "test-token")

        # Verify result
        self.assertEqual(len(issues), 2)  # PR should be filtered out

        self.assertEqual(issues[0]["number"], 1)
        self.assertEqual(issues[0]["title"], "Test Issue 1")
        self.assertEqual(issues[0]["state"], "open")
        self.assertEqual(issues[0]["html_url"], "https://github.com/test-user/test-repo/issues/1")
        self.assertEqual(issues[0]["body"], "Test issue body")
        self.assertEqual(issues[0]["user"], "test-user")
        self.assertEqual(issues[0]["labels"], ["bug", "enhancement"])
        self.assertEqual(issues[0]["assignees"], ["assignee1", "assignee2"])
        self.assertEqual(issues[0]["comments"], 2)

        self.assertEqual(issues[1]["number"], 2)
        self.assertEqual(issues[1]["title"], "Test Issue 2")
        self.assertEqual(issues[1]["labels"], [])
        self.assertEqual(issues[1]["assignees"], [])

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_issues.assert_called_once_with(state="open")

    @mock.patch("hubqueue.issues.Github")
    def test_create_issue(self, mock_github):
        """Test creating an issue."""
        # Mock GitHub API
        mock_label = mock.MagicMock()
        mock_label.name = "bug"

        mock_assignee = mock.MagicMock()
        mock_assignee.login = "assignee1"

        mock_issue = mock.MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_issue.created_at = "2023-01-01T00:00:00Z"
        mock_issue.html_url = "https://github.com/test-user/test-repo/issues/1"
        mock_issue.body = "Test issue body"
        mock_issue.user.login = "test-user"
        mock_issue.labels = [mock_label]
        mock_issue.assignees = [mock_assignee]

        mock_repo = mock.MagicMock()
        mock_repo.create_issue.return_value = mock_issue

        mock_github.return_value.get_repo.return_value = mock_repo

        # Create issue
        issue = create_issue(
            "test-user/test-repo",
            "Test Issue",
            "Test issue body",
            ["bug"],
            ["assignee1"],
            "test-token"
        )

        # Verify result
        self.assertEqual(issue["number"], 1)
        self.assertEqual(issue["title"], "Test Issue")
        self.assertEqual(issue["state"], "open")
        self.assertEqual(issue["html_url"], "https://github.com/test-user/test-repo/issues/1")
        self.assertEqual(issue["body"], "Test issue body")
        self.assertEqual(issue["user"], "test-user")
        self.assertEqual(issue["labels"], ["bug"])
        self.assertEqual(issue["assignees"], ["assignee1"])

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Test issue body",
            labels=["bug"],
            assignees=["assignee1"]
        )

    @mock.patch("hubqueue.issues.Github")
    def test_list_pull_requests(self, mock_github):
        """Test listing pull requests."""
        # Mock GitHub API
        mock_pr1 = mock.MagicMock()
        mock_pr1.number = 1
        mock_pr1.title = "Test PR 1"
        mock_pr1.state = "open"
        mock_pr1.created_at = "2023-01-01T00:00:00Z"
        mock_pr1.updated_at = "2023-01-02T00:00:00Z"
        mock_pr1.html_url = "https://github.com/test-user/test-repo/pull/1"
        mock_pr1.body = "Test PR body"
        mock_pr1.user.login = "test-user"
        mock_pr1.base.ref = "main"
        mock_pr1.head.ref = "feature-branch"
        mock_pr1.mergeable = True
        mock_pr1.merged = False
        mock_pr1.comments = 2
        mock_pr1.review_comments = 1
        mock_pr1.commits = 3
        mock_pr1.additions = 100
        mock_pr1.deletions = 50
        mock_pr1.changed_files = 5

        mock_pr2 = mock.MagicMock()
        mock_pr2.number = 2
        mock_pr2.title = "Test PR 2"
        mock_pr2.state = "open"
        mock_pr2.created_at = "2023-01-03T00:00:00Z"
        mock_pr2.updated_at = "2023-01-04T00:00:00Z"
        mock_pr2.html_url = "https://github.com/test-user/test-repo/pull/2"
        mock_pr2.body = "Another test PR body"
        mock_pr2.user.login = "test-user"
        mock_pr2.base.ref = "main"
        mock_pr2.head.ref = "another-branch"
        mock_pr2.mergeable = False
        mock_pr2.merged = False
        mock_pr2.comments = 0
        mock_pr2.review_comments = 0
        mock_pr2.commits = 1
        mock_pr2.additions = 10
        mock_pr2.deletions = 5
        mock_pr2.changed_files = 1

        mock_prs = [mock_pr1, mock_pr2]

        mock_repo = mock.MagicMock()
        mock_repo.get_pulls.return_value = mock_prs

        mock_github.return_value.get_repo.return_value = mock_repo

        # List pull requests
        prs = list_pull_requests("test-user/test-repo", "open", None, None, "test-token")

        # Verify result
        self.assertEqual(len(prs), 2)

        self.assertEqual(prs[0]["number"], 1)
        self.assertEqual(prs[0]["title"], "Test PR 1")
        self.assertEqual(prs[0]["state"], "open")
        self.assertEqual(prs[0]["html_url"], "https://github.com/test-user/test-repo/pull/1")
        self.assertEqual(prs[0]["body"], "Test PR body")
        self.assertEqual(prs[0]["user"], "test-user")
        self.assertEqual(prs[0]["base"], "main")
        self.assertEqual(prs[0]["head"], "feature-branch")
        self.assertEqual(prs[0]["mergeable"], True)
        self.assertEqual(prs[0]["merged"], False)
        self.assertEqual(prs[0]["comments"], 2)
        self.assertEqual(prs[0]["review_comments"], 1)
        self.assertEqual(prs[0]["commits"], 3)
        self.assertEqual(prs[0]["additions"], 100)
        self.assertEqual(prs[0]["deletions"], 50)
        self.assertEqual(prs[0]["changed_files"], 5)

        self.assertEqual(prs[1]["number"], 2)
        self.assertEqual(prs[1]["title"], "Test PR 2")
        self.assertEqual(prs[1]["head"], "another-branch")
        self.assertEqual(prs[1]["mergeable"], False)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_pulls.assert_called_once_with(state="open")

    @mock.patch("subprocess.run")
    @mock.patch("os.path.isdir")
    @mock.patch("hubqueue.issues.Github")
    def test_checkout_pull_request(self, mock_github, mock_isdir, mock_run):
        """Test checking out a pull request."""
        # Mock GitHub API
        mock_pr = mock.MagicMock()
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.base.ref = "main"
        mock_pr.head.ref = "feature-branch"
        mock_pr.user.login = "test-user"
        mock_pr.html_url = "https://github.com/test-user/test-repo/pull/1"

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github.return_value.get_repo.return_value = mock_repo

        # Mock os.path.isdir to return True for .git directory
        mock_isdir.return_value = True

        # Mock subprocess.run
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        # Checkout pull request
        pr_info = checkout_pull_request("test-user/test-repo", 1, self.temp_dir, "test-token")

        # Verify result
        self.assertEqual(pr_info["number"], 1)
        self.assertEqual(pr_info["title"], "Test PR")
        self.assertEqual(pr_info["branch"], "pr-1")
        self.assertEqual(pr_info["base"], "main")
        self.assertEqual(pr_info["head"], "feature-branch")
        self.assertEqual(pr_info["user"], "test-user")
        self.assertEqual(pr_info["html_url"], "https://github.com/test-user/test-repo/pull/1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_pull.assert_called_once_with(1)

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(
            ["git", "fetch", "origin", "pull/1/head:pr-1"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            ["git", "checkout", "pr-1"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
            text=True
        )

    @mock.patch("hubqueue.issues.Github")
    def test_get_issue(self, mock_github):
        """Test getting an issue."""
        # Mock GitHub API
        mock_comment1 = mock.MagicMock()
        mock_comment1.id = 1
        mock_comment1.user.login = "commenter1"
        mock_comment1.body = "Test comment 1"
        mock_comment1.created_at = "2023-01-02T00:00:00Z"
        mock_comment1.updated_at = "2023-01-02T00:00:00Z"

        mock_comment2 = mock.MagicMock()
        mock_comment2.id = 2
        mock_comment2.user.login = "commenter2"
        mock_comment2.body = "Test comment 2"
        mock_comment2.created_at = "2023-01-03T00:00:00Z"
        mock_comment2.updated_at = "2023-01-03T00:00:00Z"

        mock_label1 = mock.MagicMock()
        mock_label1.name = "bug"
        mock_label2 = mock.MagicMock()
        mock_label2.name = "enhancement"

        mock_assignee = mock.MagicMock()
        mock_assignee.login = "assignee1"

        mock_issue = mock.MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_issue.created_at = "2023-01-01T00:00:00Z"
        mock_issue.updated_at = "2023-01-03T00:00:00Z"
        mock_issue.html_url = "https://github.com/test-user/test-repo/issues/1"
        mock_issue.body = "Test issue body"
        mock_issue.user.login = "test-user"
        mock_issue.labels = [mock_label1, mock_label2]
        mock_issue.assignees = [mock_assignee]
        mock_issue.pull_request = None
        mock_issue.get_comments.return_value = [mock_comment1, mock_comment2]

        mock_repo = mock.MagicMock()
        mock_repo.get_issue.return_value = mock_issue

        mock_github.return_value.get_repo.return_value = mock_repo

        # Get issue
        issue = get_issue("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertEqual(issue["number"], 1)
        self.assertEqual(issue["title"], "Test Issue")
        self.assertEqual(issue["state"], "open")
        self.assertEqual(issue["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(issue["updated_at"], "2023-01-03T00:00:00Z")
        self.assertEqual(issue["html_url"], "https://github.com/test-user/test-repo/issues/1")
        self.assertEqual(issue["body"], "Test issue body")
        self.assertEqual(issue["user"], "test-user")
        self.assertEqual(issue["labels"], ["bug", "enhancement"])
        self.assertEqual(issue["assignees"], ["assignee1"])

        # Verify comments
        self.assertEqual(len(issue["comments"]), 2)
        self.assertEqual(issue["comments"][0]["id"], 1)
        self.assertEqual(issue["comments"][0]["user"], "commenter1")
        self.assertEqual(issue["comments"][0]["body"], "Test comment 1")
        self.assertEqual(issue["comments"][0]["created_at"], "2023-01-02T00:00:00Z")

        self.assertEqual(issue["comments"][1]["id"], 2)
        self.assertEqual(issue["comments"][1]["user"], "commenter2")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_issue.assert_called_once_with(1)
        mock_issue.get_comments.assert_called_once()

    @mock.patch("hubqueue.issues.Github")
    def test_get_pull_request(self, mock_github):
        """Test getting a pull request."""
        # Mock GitHub API
        mock_comment1 = mock.MagicMock()
        mock_comment1.id = 1
        mock_comment1.user.login = "commenter1"
        mock_comment1.body = "Test comment 1"
        mock_comment1.created_at = "2023-01-02T00:00:00Z"
        mock_comment1.updated_at = "2023-01-02T00:00:00Z"

        mock_review_comment1 = mock.MagicMock()
        mock_review_comment1.id = 2
        mock_review_comment1.user.login = "reviewer1"
        mock_review_comment1.body = "Test review comment"
        mock_review_comment1.path = "file.py"
        mock_review_comment1.position = 10
        mock_review_comment1.created_at = "2023-01-03T00:00:00Z"
        mock_review_comment1.updated_at = "2023-01-03T00:00:00Z"

        mock_commit1 = mock.MagicMock()
        mock_commit1.sha = "abc1234567890"
        mock_commit1.commit.message = "Test commit message"
        mock_commit1.commit.author.name = "Test Author"
        mock_commit1.commit.author.date = "2023-01-01T00:00:00Z"

        mock_pr = mock.MagicMock()
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.created_at = "2023-01-01T00:00:00Z"
        mock_pr.updated_at = "2023-01-03T00:00:00Z"
        mock_pr.html_url = "https://github.com/test-user/test-repo/pull/1"
        mock_pr.body = "Test PR body"
        mock_pr.user.login = "test-user"
        mock_pr.base.ref = "main"
        mock_pr.head.ref = "feature-branch"
        mock_pr.mergeable = True
        mock_pr.merged = False
        mock_pr.additions = 100
        mock_pr.deletions = 50
        mock_pr.changed_files = 5
        mock_pr.get_issue_comments.return_value = [mock_comment1]
        mock_pr.get_review_comments.return_value = [mock_review_comment1]
        mock_pr.get_commits.return_value = [mock_commit1]

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github.return_value.get_repo.return_value = mock_repo

        # Get pull request
        pr = get_pull_request("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertEqual(pr["number"], 1)
        self.assertEqual(pr["title"], "Test PR")
        self.assertEqual(pr["state"], "open")
        self.assertEqual(pr["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(pr["updated_at"], "2023-01-03T00:00:00Z")
        self.assertEqual(pr["html_url"], "https://github.com/test-user/test-repo/pull/1")
        self.assertEqual(pr["body"], "Test PR body")
        self.assertEqual(pr["user"], "test-user")
        self.assertEqual(pr["base"], "main")
        self.assertEqual(pr["head"], "feature-branch")
        self.assertEqual(pr["mergeable"], True)
        self.assertEqual(pr["merged"], False)
        self.assertEqual(pr["additions"], 100)
        self.assertEqual(pr["deletions"], 50)
        self.assertEqual(pr["changed_files"], 5)

        # Verify comments
        self.assertEqual(len(pr["comments"]), 1)
        self.assertEqual(pr["comments"][0]["id"], 1)
        self.assertEqual(pr["comments"][0]["user"], "commenter1")
        self.assertEqual(pr["comments"][0]["body"], "Test comment 1")

        # Verify review comments
        self.assertEqual(len(pr["review_comments"]), 1)
        self.assertEqual(pr["review_comments"][0]["id"], 2)
        self.assertEqual(pr["review_comments"][0]["user"], "reviewer1")
        self.assertEqual(pr["review_comments"][0]["path"], "file.py")
        self.assertEqual(pr["review_comments"][0]["position"], 10)

        # Verify commits
        self.assertEqual(len(pr["commits"]), 1)
        self.assertEqual(pr["commits"][0]["sha"], "abc1234567890")
        self.assertEqual(pr["commits"][0]["message"], "Test commit message")
        self.assertEqual(pr["commits"][0]["author"], "Test Author")
        self.assertEqual(pr["commits"][0]["date"], "2023-01-01T00:00:00Z")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_pull.assert_called_once_with(1)
        mock_pr.get_issue_comments.assert_called_once()
        mock_pr.get_review_comments.assert_called_once()
        mock_pr.get_commits.assert_called_once()
