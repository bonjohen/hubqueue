"""
Tests for the projects module.
"""
import tempfile
import os
from unittest import TestCase, mock

from hubqueue.projects import (
    list_project_boards, get_project_board, create_project_board,
    create_project_column, add_issue_to_project, add_pr_to_project,
    add_note_to_project, move_project_card, delete_project_card,
    delete_project_column, delete_project_board, create_project_from_template,
    configure_project_automation
)


class TestProjects(TestCase):
    """Test project management functions."""

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

    @mock.patch("hubqueue.projects.Github")
    def test_list_project_boards(self, mock_github):
        """Test listing project boards."""
        # Mock GitHub API
        mock_column1 = mock.MagicMock()
        mock_column1.id = 1
        mock_column1.name = "To Do"
        mock_column1.cards_url = "https://api.github.com/projects/columns/1/cards"

        mock_column2 = mock.MagicMock()
        mock_column2.id = 2
        mock_column2.name = "In Progress"
        mock_column2.cards_url = "https://api.github.com/projects/columns/2/cards"

        mock_project1 = mock.MagicMock()
        mock_project1.id = 1
        mock_project1.name = "Project 1"
        mock_project1.body = "Test Project 1"
        mock_project1.state = "open"
        mock_project1.created_at = "2023-01-01T00:00:00Z"
        mock_project1.updated_at = "2023-01-02T00:00:00Z"
        mock_project1.html_url = "https://github.com/test-user/test-repo/projects/1"
        mock_project1.get_columns.return_value = [mock_column1, mock_column2]

        mock_project2 = mock.MagicMock()
        mock_project2.id = 2
        mock_project2.name = "Project 2"
        mock_project2.body = "Test Project 2"
        mock_project2.state = "open"
        mock_project2.created_at = "2023-01-03T00:00:00Z"
        mock_project2.updated_at = "2023-01-04T00:00:00Z"
        mock_project2.html_url = "https://github.com/test-user/test-repo/projects/2"
        mock_project2.get_columns.return_value = []

        mock_repo = mock.MagicMock()
        mock_repo.get_projects.return_value = [mock_project1, mock_project2]

        mock_github.return_value.get_repo.return_value = mock_repo

        # List project boards
        projects = list_project_boards("test-user/test-repo", "test-token")

        # Verify result
        self.assertEqual(len(projects), 2)

        self.assertEqual(projects[0]["id"], 1)
        self.assertEqual(projects[0]["name"], "Project 1")
        self.assertEqual(projects[0]["body"], "Test Project 1")
        self.assertEqual(projects[0]["state"], "open")
        self.assertEqual(projects[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(projects[0]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(projects[0]["html_url"], "https://github.com/test-user/test-repo/projects/1")
        self.assertEqual(len(projects[0]["columns"]), 2)
        self.assertEqual(projects[0]["columns"][0]["id"], 1)
        self.assertEqual(projects[0]["columns"][0]["name"], "To Do")
        self.assertEqual(projects[0]["columns"][0]["cards_url"], "https://api.github.com/projects/columns/1/cards")

        self.assertEqual(projects[1]["id"], 2)
        self.assertEqual(projects[1]["name"], "Project 2")
        self.assertEqual(len(projects[1]["columns"]), 0)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_projects.assert_called_once()
        mock_project1.get_columns.assert_called_once()
        mock_project2.get_columns.assert_called_once()

    @mock.patch("hubqueue.projects.Github")
    def test_get_project_board(self, mock_github):
        """Test getting a project board."""
        # Mock GitHub API
        mock_card1 = mock.MagicMock()
        mock_card1.id = 1
        mock_card1.note = "Test note"
        mock_card1.created_at = "2023-01-01T00:00:00Z"
        mock_card1.updated_at = "2023-01-01T00:00:00Z"
        mock_card1.content_url = None

        mock_card2 = mock.MagicMock()
        mock_card2.id = 2
        mock_card2.note = None
        mock_card2.created_at = "2023-01-02T00:00:00Z"
        mock_card2.updated_at = "2023-01-02T00:00:00Z"
        mock_card2.content_url = "https://api.github.com/repos/test-user/test-repo/issues/1"

        mock_issue = mock.MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"

        mock_column1 = mock.MagicMock()
        mock_column1.id = 1
        mock_column1.name = "To Do"
        mock_column1.cards_url = "https://api.github.com/projects/columns/1/cards"
        mock_column1.get_cards.return_value = [mock_card1, mock_card2]

        mock_column2 = mock.MagicMock()
        mock_column2.id = 2
        mock_column2.name = "In Progress"
        mock_column2.cards_url = "https://api.github.com/projects/columns/2/cards"
        mock_column2.get_cards.return_value = []

        mock_project = mock.MagicMock()
        mock_project.id = 1
        mock_project.name = "Project 1"
        mock_project.body = "Test Project 1"
        mock_project.state = "open"
        mock_project.created_at = "2023-01-01T00:00:00Z"
        mock_project.updated_at = "2023-01-02T00:00:00Z"
        mock_project.html_url = "https://github.com/test-user/test-repo/projects/1"
        mock_project.get_columns.return_value = [mock_column1, mock_column2]

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project
        mock_repo.get_issue.return_value = mock_issue

        mock_github.return_value.get_repo.return_value = mock_repo

        # Get project board
        project = get_project_board("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertEqual(project["id"], 1)
        self.assertEqual(project["name"], "Project 1")
        self.assertEqual(project["body"], "Test Project 1")
        self.assertEqual(project["state"], "open")
        self.assertEqual(project["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(project["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(project["html_url"], "https://github.com/test-user/test-repo/projects/1")

        # Verify columns
        self.assertEqual(len(project["columns"]), 2)
        self.assertEqual(project["columns"][0]["id"], 1)
        self.assertEqual(project["columns"][0]["name"], "To Do")
        self.assertEqual(project["columns"][0]["cards_url"], "https://api.github.com/projects/columns/1/cards")

        # Verify cards
        self.assertEqual(len(project["columns"][0]["cards"]), 2)
        self.assertEqual(project["columns"][0]["cards"][0]["id"], 1)
        self.assertEqual(project["columns"][0]["cards"][0]["note"], "Test note")
        self.assertEqual(project["columns"][0]["cards"][0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(project["columns"][0]["cards"][0]["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(project["columns"][0]["cards"][0]["content_url"], None)

        self.assertEqual(project["columns"][0]["cards"][1]["id"], 2)
        self.assertEqual(project["columns"][0]["cards"][1]["note"], None)
        self.assertEqual(project["columns"][0]["cards"][1]["content_url"], "https://api.github.com/repos/test-user/test-repo/issues/1")
        self.assertEqual(project["columns"][0]["cards"][1]["content"]["type"], "issue")
        self.assertEqual(project["columns"][0]["cards"][1]["content"]["number"], 1)
        self.assertEqual(project["columns"][0]["cards"][1]["content"]["title"], "Test Issue")
        self.assertEqual(project["columns"][0]["cards"][1]["content"]["state"], "open")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_columns.assert_called_once()
        mock_column1.get_cards.assert_called_once()
        mock_column2.get_cards.assert_called_once()
        mock_repo.get_issue.assert_called_once_with(1)

    @mock.patch("hubqueue.projects.Github")
    def test_create_project_board(self, mock_github):
        """Test creating a project board."""
        # Mock GitHub API
        mock_project = mock.MagicMock()
        mock_project.id = 1
        mock_project.name = "Test Project"
        mock_project.body = "Test Project Description"
        mock_project.state = "open"
        mock_project.created_at = "2023-01-01T00:00:00Z"
        mock_project.updated_at = "2023-01-01T00:00:00Z"
        mock_project.html_url = "https://github.com/test-user/test-repo/projects/1"

        mock_repo = mock.MagicMock()
        mock_repo.create_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Create project board
        project = create_project_board("test-user/test-repo", "Test Project", "Test Project Description", "test-token")

        # Verify result
        self.assertEqual(project["id"], 1)
        self.assertEqual(project["name"], "Test Project")
        self.assertEqual(project["body"], "Test Project Description")
        self.assertEqual(project["state"], "open")
        self.assertEqual(project["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(project["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(project["html_url"], "https://github.com/test-user/test-repo/projects/1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.create_project.assert_called_once_with("Test Project", "Test Project Description")

    @mock.patch("hubqueue.projects.Github")
    def test_create_project_column(self, mock_github):
        """Test creating a project column."""
        # Mock GitHub API
        mock_column = mock.MagicMock()
        mock_column.id = 1
        mock_column.name = "To Do"
        mock_column.cards_url = "https://api.github.com/projects/columns/1/cards"

        mock_project = mock.MagicMock()
        mock_project.create_column.return_value = mock_column

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Create project column
        column = create_project_column("test-user/test-repo", 1, "To Do", "test-token")

        # Verify result
        self.assertEqual(column["id"], 1)
        self.assertEqual(column["name"], "To Do")
        self.assertEqual(column["cards_url"], "https://api.github.com/projects/columns/1/cards")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.create_column.assert_called_once_with("To Do")

    @mock.patch("hubqueue.projects.Github")
    def test_add_issue_to_project(self, mock_github):
        """Test adding an issue to a project."""
        # Mock GitHub API
        mock_card = mock.MagicMock()
        mock_card.id = 1
        mock_card.note = None
        mock_card.created_at = "2023-01-01T00:00:00Z"
        mock_card.updated_at = "2023-01-01T00:00:00Z"
        mock_card.content_url = "https://api.github.com/repos/test-user/test-repo/issues/1"

        mock_issue = mock.MagicMock()
        mock_issue.id = 101
        mock_issue.number = 1

        mock_column = mock.MagicMock()
        mock_column.create_card.return_value = mock_card

        mock_project = mock.MagicMock()
        mock_project.get_column.return_value = mock_column

        mock_repo = mock.MagicMock()
        mock_repo.get_issue.return_value = mock_issue
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Add issue to project
        card = add_issue_to_project("test-user/test-repo", 1, 2, 1, "test-token")

        # Verify result
        self.assertEqual(card["id"], 1)
        self.assertEqual(card["note"], None)
        self.assertEqual(card["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["content_url"], "https://api.github.com/repos/test-user/test-repo/issues/1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_issue.assert_called_once_with(1)
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_column.assert_called_once_with(2)
        mock_column.create_card.assert_called_once_with(content_id=101, content_type="Issue")

    @mock.patch("hubqueue.projects.Github")
    def test_add_pr_to_project(self, mock_github):
        """Test adding a pull request to a project."""
        # Mock GitHub API
        mock_card = mock.MagicMock()
        mock_card.id = 1
        mock_card.note = None
        mock_card.created_at = "2023-01-01T00:00:00Z"
        mock_card.updated_at = "2023-01-01T00:00:00Z"
        mock_card.content_url = "https://api.github.com/repos/test-user/test-repo/pulls/1"

        mock_pr = mock.MagicMock()
        mock_pr.id = 101
        mock_pr.number = 1

        mock_column = mock.MagicMock()
        mock_column.create_card.return_value = mock_card

        mock_project = mock.MagicMock()
        mock_project.get_column.return_value = mock_column

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Add PR to project
        card = add_pr_to_project("test-user/test-repo", 1, 2, 1, "test-token")

        # Verify result
        self.assertEqual(card["id"], 1)
        self.assertEqual(card["note"], None)
        self.assertEqual(card["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["content_url"], "https://api.github.com/repos/test-user/test-repo/pulls/1")

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_pull.assert_called_once_with(1)
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_column.assert_called_once_with(2)
        mock_column.create_card.assert_called_once_with(content_id=101, content_type="PullRequest")

    @mock.patch("hubqueue.projects.Github")
    def test_add_note_to_project(self, mock_github):
        """Test adding a note to a project."""
        # Mock GitHub API
        mock_card = mock.MagicMock()
        mock_card.id = 1
        mock_card.note = "Test note"
        mock_card.created_at = "2023-01-01T00:00:00Z"
        mock_card.updated_at = "2023-01-01T00:00:00Z"
        mock_card.content_url = None

        mock_column = mock.MagicMock()
        mock_column.create_card.return_value = mock_card

        mock_project = mock.MagicMock()
        mock_project.get_column.return_value = mock_column

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Add note to project
        card = add_note_to_project("test-user/test-repo", 1, 2, "Test note", "test-token")

        # Verify result
        self.assertEqual(card["id"], 1)
        self.assertEqual(card["note"], "Test note")
        self.assertEqual(card["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(card["content_url"], None)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_column.assert_called_once_with(2)
        mock_column.create_card.assert_called_once_with(note="Test note")

    @mock.patch("hubqueue.projects.Github")
    @mock.patch("hubqueue.projects.GithubException", new=Exception)
    def test_move_project_card(self, mock_github):
        """Test moving a project card."""
        # Mock GitHub API
        mock_card = mock.MagicMock()

        mock_column1 = mock.MagicMock()
        mock_column1.get_card.side_effect = Exception("Card not found")

        mock_column2 = mock.MagicMock()
        mock_column2.get_card.return_value = mock_card

        mock_target_column = mock.MagicMock()

        mock_project = mock.MagicMock()
        mock_project.get_columns.return_value = [mock_column1, mock_column2]
        mock_project.get_column.return_value = mock_target_column

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Move card
        result = move_project_card("test-user/test-repo", 1, 2, 3, "top", "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_column.assert_called_once_with(3)
        mock_card.move.assert_called_once_with(position="top", column=mock_target_column)

    @mock.patch("hubqueue.projects.Github")
    @mock.patch("hubqueue.projects.GithubException", new=Exception)
    def test_delete_project_card(self, mock_github):
        """Test deleting a project card."""
        # Mock GitHub API
        mock_card = mock.MagicMock()

        mock_column1 = mock.MagicMock()
        mock_column1.get_card.side_effect = Exception("Card not found")

        mock_column2 = mock.MagicMock()
        mock_column2.get_card.return_value = mock_card

        mock_project = mock.MagicMock()
        mock_project.get_columns.return_value = [mock_column1, mock_column2]

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Delete card
        result = delete_project_card("test-user/test-repo", 1, 2, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_card.delete.assert_called_once()

    @mock.patch("hubqueue.projects.Github")
    def test_delete_project_column(self, mock_github):
        """Test deleting a project column."""
        # Mock GitHub API
        mock_column = mock.MagicMock()

        mock_project = mock.MagicMock()
        mock_project.get_column.return_value = mock_column

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Delete column
        result = delete_project_column("test-user/test-repo", 1, 2, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.get_column.assert_called_once_with(2)
        mock_column.delete.assert_called_once()

    @mock.patch("hubqueue.projects.Github")
    def test_delete_project_board(self, mock_github):
        """Test deleting a project board."""
        # Mock GitHub API
        mock_project = mock.MagicMock()

        mock_repo = mock.MagicMock()
        mock_repo.get_project.return_value = mock_project

        mock_github.return_value.get_repo.return_value = mock_repo

        # Delete project
        result = delete_project_board("test-user/test-repo", 1, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_project.assert_called_once_with(1)
        mock_project.delete.assert_called_once()

    @mock.patch("hubqueue.projects.Github")
    def test_create_project_from_template(self, mock_github):
        """Test creating a project from a template."""
        # Mock create_project_board by patching the functions it calls
        with mock.patch("hubqueue.projects.create_project_board") as mock_create_project:
            with mock.patch("hubqueue.projects.create_project_column") as mock_create_column:
                with mock.patch("hubqueue.projects.get_project_board") as mock_get_project:
                    # Mock create_project_board
                    mock_create_project.return_value = {
                        "id": 1,
                        "name": "Test Project",
                        "body": "Project created from basic template",
                        "state": "open",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "html_url": "https://github.com/test-user/test-repo/projects/1",
                    }

                    # Mock get_project_board
                    mock_get_project.return_value = {
                        "id": 1,
                        "name": "Test Project",
                        "body": "Project created from basic template",
                        "state": "open",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "html_url": "https://github.com/test-user/test-repo/projects/1",
                        "columns": [
                            {
                                "id": 1,
                                "name": "To Do",
                                "cards_url": "https://api.github.com/projects/columns/1/cards",
                                "cards": [],
                            },
                            {
                                "id": 2,
                                "name": "In Progress",
                                "cards_url": "https://api.github.com/projects/columns/2/cards",
                                "cards": [],
                            },
                            {
                                "id": 3,
                                "name": "Done",
                                "cards_url": "https://api.github.com/projects/columns/3/cards",
                                "cards": [],
                            },
                        ],
                    }

                    # Create project from template
                    project = create_project_from_template("test-user/test-repo", "Test Project", "basic", "test-token")

                    # Verify result
                    self.assertEqual(project["id"], 1)
                    self.assertEqual(project["name"], "Test Project")
                    self.assertEqual(len(project["columns"]), 3)
                    self.assertEqual(project["columns"][0]["name"], "To Do")
                    self.assertEqual(project["columns"][1]["name"], "In Progress")
                    self.assertEqual(project["columns"][2]["name"], "Done")

                    # Verify API calls
                    mock_create_project.assert_called_once_with(
                        "test-user/test-repo", "Test Project", "Project created from basic template", "test-token"
                    )
                    self.assertEqual(mock_create_column.call_count, 3)
                    mock_create_column.assert_any_call("test-user/test-repo", 1, "To Do", "test-token")
                    mock_create_column.assert_any_call("test-user/test-repo", 1, "In Progress", "test-token")
                    mock_create_column.assert_any_call("test-user/test-repo", 1, "Done", "test-token")
                    mock_get_project.assert_called_once_with("test-user/test-repo", 1, "test-token")
