"""
Tests for the wizard module.
"""
import os
import sys
import tempfile
from unittest import TestCase, mock

from hubqueue.wizard import (
    Wizard, RepositoryWizard, IssueWizard, ReleaseWizard,
    run_repository_wizard, run_issue_wizard, run_release_wizard
)


class TestWizard(TestCase):
    """Test wizard classes."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

        # Mock is_interactive
        self.interactive_patcher = mock.patch('hubqueue.ui.is_interactive', return_value=True)
        self.interactive_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.interactive_patcher.stop()

        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_wizard_init(self):
        """Test Wizard initialization."""
        wizard = Wizard(title="Test Wizard", description="Test description", steps=["step1", "step2"])
        self.assertEqual(wizard.title, "Test Wizard")
        self.assertEqual(wizard.description, "Test description")
        self.assertEqual(wizard.steps, ["step1", "step2"])
        self.assertEqual(wizard.current_step, 0)
        self.assertEqual(wizard.data, {})
        self.assertFalse(wizard.cancelled)

    @mock.patch('hubqueue.ui.is_interactive', return_value=False)
    def test_wizard_run_non_interactive(self, mock_interactive):
        """Test Wizard run in non-interactive mode."""
        wizard = Wizard(title="Test Wizard", description="Test description", steps=["step1", "step2"])
        result = wizard.run()
        self.assertEqual(result, {})

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.clear_screen')
    @mock.patch('hubqueue.ui.print_header')
    @mock.patch('hubqueue.ui.print_info')
    @mock.patch('hubqueue.ui.print_color')
    @mock.patch('hubqueue.ui.print_success')
    def test_wizard_run(self, mock_success, mock_color, mock_info, mock_header, mock_clear, mock_interactive):
        """Test Wizard run."""
        # Create a test wizard with a step method
        class TestWizard(Wizard):
            def step_step1(self):
                self.data["step1"] = "done"
                return True

            def step_step2(self):
                self.data["step2"] = "done"
                return True

        wizard = TestWizard(title="Test Wizard", description="Test description", steps=["step1", "step2"])
        result = wizard.run()

        # Verify result
        self.assertEqual(result, {"step1": "done", "step2": "done"})
        self.assertEqual(wizard.current_step, 2)
        self.assertFalse(wizard.cancelled)

        # Verify method calls
        mock_clear.assert_called_once()
        mock_header.assert_called_once_with("Test Wizard")
        mock_info.assert_called_once_with("Test description")
        mock_success.assert_called_once_with("Test Wizard completed successfully!")

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.clear_screen')
    @mock.patch('hubqueue.ui.print_header')
    @mock.patch('hubqueue.ui.print_info')
    @mock.patch('hubqueue.ui.print_color')
    @mock.patch('hubqueue.ui.print_warning')
    @mock.patch('hubqueue.ui.confirm')
    def test_wizard_run_cancel(self, mock_confirm, mock_warning, mock_color, mock_info, mock_header, mock_clear, mock_interactive):
        """Test Wizard run with cancellation."""
        # Create a test wizard with a step method that returns False
        class TestWizard(Wizard):
            def step_step1(self):
                self.data["step1"] = "done"
                return False

        # Mock confirm to return True (confirm cancellation)
        mock_confirm.return_value = True

        wizard = TestWizard(title="Test Wizard", description="Test description", steps=["step1", "step2"])
        result = wizard.run()

        # Verify result
        self.assertEqual(result, {"step1": "done"})
        self.assertEqual(wizard.current_step, 0)
        self.assertTrue(wizard.cancelled)

        # Verify method calls
        mock_clear.assert_called_once()
        mock_header.assert_called_once_with("Test Wizard")
        mock_info.assert_called_once_with("Test description")
        mock_warning.assert_called_once_with("Wizard cancelled.")

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.clear_screen')
    @mock.patch('hubqueue.ui.print_header')
    @mock.patch('hubqueue.ui.print_info')
    @mock.patch('hubqueue.ui.print_color')
    @mock.patch('hubqueue.ui.print_warning')
    def test_wizard_run_keyboard_interrupt(self, mock_warning, mock_color, mock_info, mock_header, mock_clear, mock_interactive):
        """Test Wizard run with KeyboardInterrupt."""
        # Create a test wizard with a step method that raises KeyboardInterrupt
        class TestWizard(Wizard):
            def step_step1(self):
                raise KeyboardInterrupt()

        wizard = TestWizard(title="Test Wizard", description="Test description", steps=["step1", "step2"])
        result = wizard.run()

        # Verify result
        self.assertEqual(result, {})
        self.assertEqual(wizard.current_step, 0)
        self.assertTrue(wizard.cancelled)

        # Verify method calls
        mock_clear.assert_called_once()
        mock_header.assert_called_once_with("Test Wizard")
        mock_info.assert_called_once_with("Test description")
        mock_warning.assert_called_once_with("\nWizard cancelled.")

    @mock.patch('hubqueue.wizard.RepositoryWizard.run')
    def test_run_repository_wizard(self, mock_run):
        """Test run_repository_wizard function."""
        mock_run.return_value = {"name": "test-repo"}
        result = run_repository_wizard()
        self.assertEqual(result, {"name": "test-repo"})
        mock_run.assert_called_once()

    @mock.patch('hubqueue.wizard.IssueWizard.run')
    def test_run_issue_wizard(self, mock_run):
        """Test run_issue_wizard function."""
        mock_run.return_value = {"title": "test-issue"}
        result = run_issue_wizard("owner/repo")
        self.assertEqual(result, {"title": "test-issue"})
        mock_run.assert_called_once()

    @mock.patch('hubqueue.wizard.ReleaseWizard.run')
    def test_run_release_wizard(self, mock_run):
        """Test run_release_wizard function."""
        mock_run.return_value = {"tag": "v1.0.0"}
        result = run_release_wizard("owner/repo")
        self.assertEqual(result, {"tag": "v1.0.0"})
        mock_run.assert_called_once()

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.prompt')
    @mock.patch('hubqueue.ui.select')
    @mock.patch('hubqueue.ui.confirm')
    @mock.patch('hubqueue.ui.multi_select')
    def test_repository_wizard(self, mock_multi_select, mock_confirm, mock_select, mock_prompt, mock_interactive):
        """Test RepositoryWizard."""
        # Mock UI functions
        mock_prompt.side_effect = ["test-repo", "owner", "Test repository", "main"]
        mock_select.side_effect = ["Personal", "Public", "Standard"]
        mock_confirm.side_effect = [True, True, True, True]
        mock_multi_select.return_value = ["Issues", "Projects", "Wiki"]

        # Create and run wizard
        wizard = RepositoryWizard()

        # Mock the data dictionary
        wizard.data = {}

        # Test step_repository_info
        mock_prompt.side_effect = ["test-repo", "owner", "Test repository"]
        mock_select.side_effect = ["Personal", "Public"]
        result = wizard.step_repository_info()
        self.assertTrue(result)
        self.assertEqual(wizard.data["name"], "test-repo")
        self.assertEqual(wizard.data["owner"], "owner")
        self.assertEqual(wizard.data["owner_type"], "Personal")
        self.assertEqual(wizard.data["description"], "Test repository")
        self.assertEqual(wizard.data["visibility"], "public")

        # Test step_repository_settings
        result = wizard.step_repository_settings()
        self.assertTrue(result)
        self.assertEqual(wizard.data["features"], ["Issues", "Projects", "Wiki"])
        self.assertEqual(wizard.data["default_branch"], "main")

        # Test step_repository_files
        result = wizard.step_repository_files()
        self.assertTrue(result)
        self.assertTrue(wizard.data["create_readme"])
        self.assertEqual(wizard.data["readme_template"], "Standard")
        self.assertTrue(wizard.data["create_gitignore"])
        self.assertTrue(wizard.data["create_license"])

        # Test step_repository_collaborators
        mock_prompt.side_effect = ["collaborator", "collaborator2"]
        mock_select.side_effect = ["Write", "Read"]
        mock_confirm.side_effect = [True, True, False]

        result = wizard.step_repository_collaborators()
        self.assertTrue(result)
        self.assertEqual(len(wizard.data["collaborators"]), 2)
        self.assertEqual(wizard.data["collaborators"][0]["username"], "collaborator")
        self.assertEqual(wizard.data["collaborators"][0]["permission"], "write")
        self.assertEqual(wizard.data["collaborators"][1]["username"], "collaborator2")
        self.assertEqual(wizard.data["collaborators"][1]["permission"], "read")

        # Test step_repository_confirmation
        mock_confirm.return_value = True
        result = wizard.step_repository_confirmation()
        self.assertTrue(result)

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.prompt')
    @mock.patch('hubqueue.ui.select')
    @mock.patch('hubqueue.ui.confirm')
    @mock.patch('hubqueue.ui.multi_select')
    def test_issue_wizard(self, mock_multi_select, mock_confirm, mock_select, mock_prompt, mock_interactive):
        """Test IssueWizard."""
        # Mock UI functions
        mock_prompt.side_effect = ["owner/repo", "Test issue", "Issue description"]
        mock_select.side_effect = ["Bug", "Medium"]
        mock_confirm.side_effect = [True, True, False]
        mock_multi_select.return_value = ["bug", "priority:medium"]

        # Create and run wizard
        wizard = IssueWizard()

        # Mock the data dictionary
        wizard.data = {}

        # Test step_repository
        mock_prompt.return_value = "owner/repo"
        result = wizard.step_repository()
        self.assertTrue(result)
        self.assertEqual(wizard.data["repo_name"], "owner/repo")

        # Test step_issue_info
        result = wizard.step_issue_info()
        self.assertTrue(result)
        self.assertEqual(wizard.data["title"], "Test issue")
        self.assertEqual(wizard.data["type"], "Bug")
        self.assertEqual(wizard.data["priority"], "Medium")

        # Test step_issue_details
        with mock.patch('hubqueue.config.edit_file', return_value="Issue description"):
            result = wizard.step_issue_details()
            self.assertTrue(result)
            self.assertEqual(wizard.data["description"], "Issue description")
            self.assertEqual(wizard.data["labels"], ["bug", "priority:medium"])
            self.assertEqual(wizard.data["assignees"], [])

        # Test step_issue_confirmation
        mock_confirm.return_value = True
        result = wizard.step_issue_confirmation()
        self.assertTrue(result)

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.prompt')
    @mock.patch('hubqueue.ui.select')
    @mock.patch('hubqueue.ui.confirm')
    def test_release_wizard(self, mock_confirm, mock_select, mock_prompt, mock_interactive):
        """Test ReleaseWizard."""
        # Mock UI functions
        mock_prompt.side_effect = ["owner/repo", "v1.0.0", "Version 1.0.0", "main", "Release notes"]
        mock_select.side_effect = ["Full Release"]
        mock_confirm.side_effect = [False, False, True]

        # Create and run wizard
        wizard = ReleaseWizard()

        # Mock the data dictionary
        wizard.data = {}

        # Test step_repository
        mock_prompt.return_value = "owner/repo"
        result = wizard.step_repository()
        self.assertTrue(result)
        self.assertEqual(wizard.data["repo_name"], "owner/repo")

        # Test step_release_info
        with mock.patch('hubqueue.config.edit_file', return_value="Release notes"):
            result = wizard.step_release_info()
            self.assertTrue(result)
            self.assertEqual(wizard.data["tag"], "v1.0.0")
            self.assertEqual(wizard.data["title"], "Version 1.0.0")
            self.assertEqual(wizard.data["target"], "main")
            self.assertEqual(wizard.data["type"], "Full Release")
            self.assertFalse(wizard.data["generate_notes"])
            self.assertEqual(wizard.data["notes"], "Release notes")

        # Test step_release_assets
        result = wizard.step_release_assets()
        self.assertTrue(result)
        self.assertEqual(wizard.data["assets"], [])

        # Test step_release_confirmation
        mock_confirm.return_value = True
        result = wizard.step_release_confirmation()
        self.assertTrue(result)
