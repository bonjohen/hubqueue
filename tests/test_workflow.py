"""
Tests for the workflow module.
"""
import tempfile
import time
from unittest import TestCase, mock

from hubqueue.workflow import (
    list_workflows, trigger_workflow, list_workflow_runs,
    get_workflow_run, monitor_workflow_run, cancel_workflow_run,
    rerun_workflow_run, list_repository_secrets, create_repository_secret,
    delete_repository_secret, list_workflow_caches, delete_workflow_cache
)


class TestWorkflow(TestCase):
    """Test workflow automation and monitoring functions."""

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

    @mock.patch("hubqueue.workflow.Github")
    def test_list_workflows(self, mock_github):
        """Test listing workflows."""
        # Mock GitHub API
        mock_workflow1 = mock.MagicMock()
        mock_workflow1.id = 1
        mock_workflow1.name = "CI"
        mock_workflow1.path = ".github/workflows/ci.yml"
        mock_workflow1.state = "active"
        mock_workflow1.created_at = "2023-01-01T00:00:00Z"
        mock_workflow1.updated_at = "2023-01-02T00:00:00Z"
        mock_workflow1.html_url = "https://github.com/test-user/test-repo/actions/workflows/ci.yml"

        mock_workflow2 = mock.MagicMock()
        mock_workflow2.id = 2
        mock_workflow2.name = "Release"
        mock_workflow2.path = ".github/workflows/release.yml"
        mock_workflow2.state = "active"
        mock_workflow2.created_at = "2023-01-03T00:00:00Z"
        mock_workflow2.updated_at = "2023-01-04T00:00:00Z"
        mock_workflow2.html_url = "https://github.com/test-user/test-repo/actions/workflows/release.yml"

        mock_repo = mock.MagicMock()
        mock_repo.get_workflows.return_value = [mock_workflow1, mock_workflow2]

        mock_github.return_value.get_repo.return_value = mock_repo

        # List workflows
        workflows = list_workflows("test-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(len(workflows), 2)

        self.assertEqual(workflows[0]["id"], 1)
        self.assertEqual(workflows[0]["name"], "CI")
        self.assertEqual(workflows[0]["path"], ".github/workflows/ci.yml")
        self.assertEqual(workflows[0]["state"], "active")
        self.assertEqual(workflows[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(workflows[0]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(workflows[0]["url"], "https://github.com/test-user/test-repo/actions/workflows/ci.yml")

        self.assertEqual(workflows[1]["id"], 2)
        self.assertEqual(workflows[1]["name"], "Release")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflows.assert_called_once()

    @mock.patch("hubqueue.workflow.Github")
    def test_trigger_workflow(self, mock_github):
        """Test triggering a workflow."""
        # Mock GitHub API
        mock_workflow = mock.MagicMock()
        mock_workflow.id = 1
        mock_workflow.name = "CI"
        mock_workflow.html_url = "https://github.com/test-user/test-repo/actions/workflows/ci.yml"
        mock_workflow.create_dispatch.return_value = mock.MagicMock(id=123)

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow.return_value = mock_workflow

        mock_github.return_value.get_repo.return_value = mock_repo

        # Trigger workflow
        run = trigger_workflow("test-user/test-repo", 1, "main", {"input1": "value1"}, "test-token")

        # Verify result
        self.assertEqual(run["workflow_id"], 1)
        self.assertEqual(run["workflow_name"], "CI")
        self.assertEqual(run["run_id"], 123)
        self.assertEqual(run["status"], "queued")
        self.assertEqual(run["url"], "https://github.com/test-user/test-repo/actions/workflows/ci.yml")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow.assert_called_once_with(1)
        mock_workflow.create_dispatch.assert_called_once_with("main", {"input1": "value1"})

    @mock.patch("hubqueue.workflow.Github")
    def test_list_workflow_runs(self, mock_github):
        """Test listing workflow runs."""
        # Mock GitHub API
        mock_run1 = mock.MagicMock()
        mock_run1.id = 1
        mock_run1.name = "CI"
        mock_run1.workflow_id = 1
        mock_run1.status = "completed"
        mock_run1.conclusion = "success"
        mock_run1.head_branch = "main"
        mock_run1.head_sha = "abc123"
        mock_run1.created_at = "2023-01-01T00:00:00Z"
        mock_run1.updated_at = "2023-01-02T00:00:00Z"
        mock_run1.html_url = "https://github.com/test-user/test-repo/actions/runs/1"

        mock_run2 = mock.MagicMock()
        mock_run2.id = 2
        mock_run2.name = "CI"
        mock_run2.workflow_id = 1
        mock_run2.status = "in_progress"
        mock_run2.conclusion = None
        mock_run2.head_branch = "feature"
        mock_run2.head_sha = "def456"
        mock_run2.created_at = "2023-01-03T00:00:00Z"
        mock_run2.updated_at = "2023-01-04T00:00:00Z"
        mock_run2.html_url = "https://github.com/test-user/test-repo/actions/runs/2"

        mock_workflow = mock.MagicMock()
        mock_workflow.get_runs.return_value = [mock_run1, mock_run2]

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow.return_value = mock_workflow
        mock_repo.get_workflow_runs.return_value = [mock_run1, mock_run2]

        mock_github.return_value.get_repo.return_value = mock_repo

        # List workflow runs
        runs = list_workflow_runs("test-user/test-repo", 1, None, None, "test-token")

        # Verify result
        self.assertEqual(len(runs), 2)

        self.assertEqual(runs[0]["id"], 1)
        self.assertEqual(runs[0]["name"], "CI")
        self.assertEqual(runs[0]["workflow_id"], 1)
        self.assertEqual(runs[0]["status"], "completed")
        self.assertEqual(runs[0]["conclusion"], "success")
        self.assertEqual(runs[0]["branch"], "main")
        self.assertEqual(runs[0]["commit"], "abc123")
        self.assertEqual(runs[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(runs[0]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(runs[0]["url"], "https://github.com/test-user/test-repo/actions/runs/1")

        self.assertEqual(runs[1]["id"], 2)
        self.assertEqual(runs[1]["status"], "in_progress")
        self.assertEqual(runs[1]["conclusion"], None)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow.assert_called_once_with(1)
        mock_workflow.get_runs.assert_called_once()

    @mock.patch("hubqueue.workflow.Github")
    def test_get_workflow_run(self, mock_github):
        """Test getting a workflow run."""
        # Mock GitHub API
        mock_step1 = mock.MagicMock()
        mock_step1.name = "Checkout"
        mock_step1.status = "completed"
        mock_step1.conclusion = "success"
        mock_step1.number = 1
        mock_step1.started_at = "2023-01-01T00:01:00Z"
        mock_step1.completed_at = "2023-01-01T00:02:00Z"

        mock_step2 = mock.MagicMock()
        mock_step2.name = "Build"
        mock_step2.status = "completed"
        mock_step2.conclusion = "success"
        mock_step2.number = 2
        mock_step2.started_at = "2023-01-01T00:02:00Z"
        mock_step2.completed_at = "2023-01-01T00:03:00Z"

        mock_job = mock.MagicMock()
        mock_job.id = 1
        mock_job.name = "build"
        mock_job.status = "completed"
        mock_job.conclusion = "success"
        mock_job.started_at = "2023-01-01T00:01:00Z"
        mock_job.completed_at = "2023-01-01T00:03:00Z"
        mock_job.get_steps.return_value = [mock_step1, mock_step2]

        mock_run = mock.MagicMock()
        mock_run.id = 1
        mock_run.name = "CI"
        mock_run.workflow_id = 1
        mock_run.status = "completed"
        mock_run.conclusion = "success"
        mock_run.head_branch = "main"
        mock_run.head_sha = "abc123"
        mock_run.created_at = "2023-01-01T00:00:00Z"
        mock_run.updated_at = "2023-01-01T00:03:00Z"
        mock_run.html_url = "https://github.com/test-user/test-repo/actions/runs/1"
        mock_run.get_jobs.return_value = [mock_job]

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run

        mock_github.return_value.get_repo.return_value = mock_repo

        # Get workflow run
        run = get_workflow_run("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertEqual(run["id"], 1)
        self.assertEqual(run["name"], "CI")
        self.assertEqual(run["workflow_id"], 1)
        self.assertEqual(run["status"], "completed")
        self.assertEqual(run["conclusion"], "success")
        self.assertEqual(run["branch"], "main")
        self.assertEqual(run["commit"], "abc123")
        self.assertEqual(run["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(run["updated_at"], "2023-01-01T00:03:00Z")
        self.assertEqual(run["url"], "https://github.com/test-user/test-repo/actions/runs/1")

        # Verify jobs
        self.assertEqual(len(run["jobs"]), 1)
        self.assertEqual(run["jobs"][0]["id"], 1)
        self.assertEqual(run["jobs"][0]["name"], "build")
        self.assertEqual(run["jobs"][0]["status"], "completed")
        self.assertEqual(run["jobs"][0]["conclusion"], "success")
        self.assertEqual(run["jobs"][0]["started_at"], "2023-01-01T00:01:00Z")
        self.assertEqual(run["jobs"][0]["completed_at"], "2023-01-01T00:03:00Z")

        # Verify steps
        self.assertEqual(len(run["jobs"][0]["steps"]), 2)
        self.assertEqual(run["jobs"][0]["steps"][0]["name"], "Checkout")
        self.assertEqual(run["jobs"][0]["steps"][0]["status"], "completed")
        self.assertEqual(run["jobs"][0]["steps"][0]["conclusion"], "success")
        self.assertEqual(run["jobs"][0]["steps"][0]["number"], 1)
        self.assertEqual(run["jobs"][0]["steps"][0]["started_at"], "2023-01-01T00:01:00Z")
        self.assertEqual(run["jobs"][0]["steps"][0]["completed_at"], "2023-01-01T00:02:00Z")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow_run.assert_called_once_with(1)
        mock_run.get_jobs.assert_called_once()
        mock_job.get_steps.assert_called_once()

    @mock.patch("hubqueue.workflow.time.sleep")
    @mock.patch("hubqueue.workflow.time.time")
    @mock.patch("hubqueue.workflow.Github")
    def test_monitor_workflow_run(self, mock_github, mock_time, mock_sleep):
        """Test monitoring a workflow run."""
        # Mock time.time to return increasing values
        mock_time.side_effect = [0, 10, 20]

        # Mock GitHub API
        mock_run = mock.MagicMock()
        mock_run.id = 1
        mock_run.name = "CI"
        mock_run.workflow_id = 1
        mock_run.status = "completed"  # Run is already completed
        mock_run.conclusion = "success"
        mock_run.head_branch = "main"
        mock_run.head_sha = "abc123"
        mock_run.created_at = "2023-01-01T00:00:00Z"
        mock_run.updated_at = "2023-01-01T00:03:00Z"
        mock_run.html_url = "https://github.com/test-user/test-repo/actions/runs/1"

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run

        mock_github.return_value.get_repo.return_value = mock_repo

        # Monitor workflow run
        run = monitor_workflow_run("test-user/test-repo", 1, 5, 300, "test-token")

        # Verify result
        self.assertEqual(run["id"], 1)
        self.assertEqual(run["name"], "CI")
        self.assertEqual(run["status"], "completed")
        self.assertEqual(run["conclusion"], "success")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow_run.assert_called_once_with(1)

        # Verify time.sleep was not called (run was already completed)
        mock_sleep.assert_not_called()

    @mock.patch("hubqueue.workflow.time.sleep")
    @mock.patch("hubqueue.workflow.time.time")
    @mock.patch("hubqueue.workflow.Github")
    def test_monitor_workflow_run_timeout(self, mock_github, mock_time, mock_sleep):
        """Test monitoring a workflow run with timeout."""
        # Mock time.time to simulate timeout
        mock_time.side_effect = [0, 100, 200, 300, 400]

        # Mock GitHub API
        mock_run = mock.MagicMock()
        mock_run.id = 1
        mock_run.name = "CI"
        mock_run.workflow_id = 1
        mock_run.status = "in_progress"  # Run is still in progress
        mock_run.conclusion = None
        mock_run.head_branch = "main"
        mock_run.head_sha = "abc123"
        mock_run.created_at = "2023-01-01T00:00:00Z"
        mock_run.updated_at = "2023-01-01T00:03:00Z"
        mock_run.html_url = "https://github.com/test-user/test-repo/actions/runs/1"

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run

        mock_github.return_value.get_repo.return_value = mock_repo

        # Monitor workflow run with timeout
        run = monitor_workflow_run("test-user/test-repo", 1, 5, 300, "test-token")

        # Verify result
        self.assertEqual(run["id"], 1)
        self.assertEqual(run["name"], "CI")
        self.assertEqual(run["status"], "in_progress")
        self.assertEqual(run["conclusion"], None)
        self.assertTrue(run["timed_out"])

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        # The actual call count depends on the implementation, but should be at least 1
        self.assertGreaterEqual(mock_repo.get_workflow_run.call_count, 1)

        # Verify time.sleep was called at least once
        self.assertGreaterEqual(mock_sleep.call_count, 1)

    @mock.patch("hubqueue.workflow.Github")
    def test_cancel_workflow_run(self, mock_github):
        """Test cancelling a workflow run."""
        # Mock GitHub API
        mock_run = mock.MagicMock()

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run

        mock_github.return_value.get_repo.return_value = mock_repo

        # Cancel workflow run
        result = cancel_workflow_run("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow_run.assert_called_once_with(1)
        mock_run.cancel.assert_called_once()

    @mock.patch("hubqueue.workflow.Github")
    def test_rerun_workflow_run(self, mock_github):
        """Test rerunning a workflow run."""
        # Mock GitHub API
        mock_run = mock.MagicMock()

        mock_repo = mock.MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run

        mock_github.return_value.get_repo.return_value = mock_repo

        # Rerun workflow run
        result = rerun_workflow_run("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_workflow_run.assert_called_once_with(1)
        mock_run.rerun.assert_called_once()

    @mock.patch("hubqueue.workflow.Github")
    def test_list_repository_secrets(self, mock_github):
        """Test listing repository secrets."""
        # Mock GitHub API
        mock_secret1 = mock.MagicMock()
        mock_secret1.name = "SECRET1"
        mock_secret1.created_at = "2023-01-01T00:00:00Z"
        mock_secret1.updated_at = "2023-01-02T00:00:00Z"

        mock_secret2 = mock.MagicMock()
        mock_secret2.name = "SECRET2"
        mock_secret2.created_at = "2023-01-03T00:00:00Z"
        mock_secret2.updated_at = "2023-01-04T00:00:00Z"

        mock_repo = mock.MagicMock()
        mock_repo.get_secrets.return_value = [mock_secret1, mock_secret2]

        mock_github.return_value.get_repo.return_value = mock_repo

        # List repository secrets
        secrets = list_repository_secrets("test-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(len(secrets), 2)

        self.assertEqual(secrets[0]["name"], "SECRET1")
        self.assertEqual(secrets[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(secrets[0]["updated_at"], "2023-01-02T00:00:00Z")

        self.assertEqual(secrets[1]["name"], "SECRET2")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_secrets.assert_called_once()

    @mock.patch("hubqueue.workflow.Github")
    def test_create_repository_secret(self, mock_github):
        """Test creating a repository secret."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()

        mock_github.return_value.get_repo.return_value = mock_repo

        # Create repository secret
        result = create_repository_secret("test-user/test-repo", "SECRET", "value", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.create_secret.assert_called_once_with("SECRET", "value")

    @mock.patch("hubqueue.workflow.Github")
    def test_delete_repository_secret(self, mock_github):
        """Test deleting a repository secret."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()

        mock_github.return_value.get_repo.return_value = mock_repo

        # Delete repository secret
        result = delete_repository_secret("test-user/test-repo", "SECRET", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.delete_secret.assert_called_once_with("SECRET")

    @mock.patch("hubqueue.workflow.Github")
    def test_list_workflow_caches(self, mock_github):
        """Test listing workflow caches."""
        # Mock GitHub API
        mock_requester = mock.MagicMock()
        mock_requester.requestJson.return_value = [{
            "actions_caches": [
                {
                    "id": 1,
                    "ref": "refs/heads/main",
                    "key": "cache-key-1",
                    "version": "v1",
                    "size_in_bytes": 1024,
                    "created_at": "2023-01-01T00:00:00Z"
                },
                {
                    "id": 2,
                    "ref": "refs/heads/feature",
                    "key": "cache-key-2",
                    "version": "v1",
                    "size_in_bytes": 2048,
                    "created_at": "2023-01-02T00:00:00Z"
                }
            ]
        }]

        mock_github._Github__requester = mock_requester
        mock_repo = mock.MagicMock()

        mock_github.return_value.get_repo.return_value = mock_repo
        mock_github.return_value._Github__requester = mock_requester

        # List workflow caches
        caches = list_workflow_caches("test-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(len(caches), 2)

        self.assertEqual(caches[0]["id"], 1)
        self.assertEqual(caches[0]["ref"], "refs/heads/main")
        self.assertEqual(caches[0]["key"], "cache-key-1")
        self.assertEqual(caches[0]["version"], "v1")
        self.assertEqual(caches[0]["size"], 1024)
        self.assertEqual(caches[0]["created_at"], "2023-01-01T00:00:00Z")

        self.assertEqual(caches[1]["id"], 2)
        self.assertEqual(caches[1]["ref"], "refs/heads/feature")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_requester.requestJson.assert_called_once_with("GET", "/repos/test-user/test-repo/actions/caches")

    @mock.patch("hubqueue.workflow.Github")
    def test_delete_workflow_cache_by_id(self, mock_github):
        """Test deleting a workflow cache by ID."""
        # Mock GitHub API
        mock_requester = mock.MagicMock()

        mock_github._Github__requester = mock_requester
        mock_repo = mock.MagicMock()

        mock_github.return_value.get_repo.return_value = mock_repo
        mock_github.return_value._Github__requester = mock_requester

        # Delete workflow cache by ID
        result = delete_workflow_cache("test-user/test-repo", 1, None, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_requester.requestJson.assert_called_once_with("DELETE", "/repos/test-user/test-repo/actions/caches/1")

    @mock.patch("hubqueue.workflow.Github")
    def test_delete_workflow_cache_by_key(self, mock_github):
        """Test deleting a workflow cache by key."""
        # Mock GitHub API
        mock_requester = mock.MagicMock()

        mock_github._Github__requester = mock_requester
        mock_repo = mock.MagicMock()

        mock_github.return_value.get_repo.return_value = mock_repo
        mock_github.return_value._Github__requester = mock_requester

        # Delete workflow cache by key
        result = delete_workflow_cache("test-user/test-repo", None, "cache-key", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_requester.requestJson.assert_called_once_with("DELETE", "/repos/test-user/test-repo/actions/caches", params={"key": "cache-key"})
