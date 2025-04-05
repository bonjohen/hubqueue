"""
Tests for the forms module.
"""
import os
import sys
import tempfile
from unittest import TestCase, mock

from hubqueue.forms import (
    Field, TextField, PasswordField, BooleanField, ChoiceField, MultiChoiceField,
    Form, RepositoryForm, IssueForm, render_form, create_repository_form, create_issue_form
)


class TestForms(TestCase):
    """Test form classes."""

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

    def test_field_init(self):
        """Test Field initialization."""
        field = Field("name", "Name", required=True, default="default", help_text="Help text")
        self.assertEqual(field.name, "name")
        self.assertEqual(field.label, "Name")
        self.assertTrue(field.required)
        self.assertEqual(field.default, "default")
        self.assertEqual(field.help_text, "Help text")
        self.assertEqual(field.validators, [])
        self.assertIsNone(field.value)

    def test_field_get_prompt_text(self):
        """Test Field get_prompt_text method."""
        # Test with required field
        field = Field("name", "Name", required=True, help_text="Help text")
        self.assertEqual(field.get_prompt_text(), "Name (required)\nHelp text")

        # Test with optional field
        field = Field("name", "Name", required=False)
        self.assertEqual(field.get_prompt_text(), "Name")

        # Test with help text
        field = Field("name", "Name", help_text="Help text")
        self.assertEqual(field.get_prompt_text(), "Name\nHelp text")

    def test_field_validate(self):
        """Test Field validate method."""
        # Test with required field
        field = Field("name", "Name", required=True)
        self.assertFalse(field.validate(None))
        self.assertFalse(field.validate(""))
        self.assertTrue(field.validate("value"))

        # Test with optional field
        field = Field("name", "Name", required=False)
        self.assertTrue(field.validate(None))
        self.assertTrue(field.validate(""))
        self.assertTrue(field.validate("value"))

        # Test with validators
        field = Field("name", "Name", validators=[
            lambda x: x == "valid" or print("Invalid value")
        ])
        self.assertFalse(field.validate("invalid"))
        self.assertTrue(field.validate("valid"))

    def test_field_to_dict(self):
        """Test Field to_dict method."""
        field = Field("name", "Name", required=True, default="default", help_text="Help text")
        field.value = "value"

        expected = {
            "name": "name",
            "label": "Name",
            "required": True,
            "default": "default",
            "help_text": "Help text",
            "value": "value",
        }

        self.assertEqual(field.to_dict(), expected)

    @mock.patch('hubqueue.ui.prompt')
    def test_text_field(self, mock_prompt):
        """Test TextField."""
        # Mock prompt
        mock_prompt.return_value = "value"

        # Create field
        field = TextField("name", "Name", required=True, min_length=3, max_length=10)

        # Test validate method
        self.assertFalse(field.validate("ab"))  # Too short
        self.assertFalse(field.validate("abcdefghijk"))  # Too long
        self.assertTrue(field.validate("abcdef"))  # Just right

        # Test render method
        result = field.render()
        self.assertEqual(result, "value")
        self.assertEqual(field.value, "value")
        mock_prompt.assert_called_once_with("Name (required)", default=None)

    @mock.patch('hubqueue.ui.password')
    def test_password_field(self, mock_password):
        """Test PasswordField."""
        # Mock password
        mock_password.return_value = "password"

        # Create field
        field = PasswordField("password", "Password", required=True, min_length=8, confirmation=True)

        # Test validate method
        self.assertFalse(field.validate("pass"))  # Too short
        self.assertTrue(field.validate("password123"))  # Just right

        # Test render method
        result = field.render()
        self.assertEqual(result, "password")
        self.assertEqual(field.value, "password")
        mock_password.assert_called_once_with("Password (required)", confirmation_prompt=True)

    @mock.patch('hubqueue.ui.confirm')
    def test_boolean_field(self, mock_confirm):
        """Test BooleanField."""
        # Mock confirm
        mock_confirm.return_value = True

        # Create field
        field = BooleanField("enabled", "Enable feature", default=False)

        # Test render method
        result = field.render()
        self.assertEqual(result, True)
        self.assertEqual(field.value, True)
        mock_confirm.assert_called_once_with("Enable feature", default=False)

    @mock.patch('hubqueue.ui.select')
    def test_choice_field(self, mock_select):
        """Test ChoiceField."""
        # Mock select
        mock_select.return_value = "option2"

        # Create field
        field = ChoiceField("choice", "Select option", choices=["option1", "option2", "option3"], default="option1")

        # Test validate method
        self.assertFalse(field.validate("option4"))  # Not in choices
        self.assertTrue(field.validate("option2"))  # In choices

        # Set up mock for render method
        field.validate = mock.MagicMock(return_value=True)

        # Test render method
        result = field.render()
        self.assertEqual(result, "option2")
        self.assertEqual(field.value, "option2")
        mock_select.assert_called_once_with("Select option", ["option1", "option2", "option3"], default="option1")

    @mock.patch('hubqueue.ui.multi_select')
    def test_multi_choice_field(self, mock_multi_select):
        """Test MultiChoiceField."""
        # Mock multi_select
        mock_multi_select.return_value = ["option1", "option3"]

        # Create field
        field = MultiChoiceField("choices", "Select options", choices=["option1", "option2", "option3"], min_choices=1, max_choices=2)

        # Create a new instance for validation tests
        validate_field = MultiChoiceField("choices", "Select options", choices=["option1", "option2", "option3"], min_choices=1, max_choices=2)

        # Test validate method
        self.assertFalse(validate_field.validate([]))  # Too few
        self.assertFalse(validate_field.validate(["option1", "option2", "option3"]))  # Too many
        self.assertFalse(validate_field.validate(["option1", "option4"]))  # Invalid choice
        self.assertTrue(validate_field.validate(["option1", "option3"]))  # Just right

        # Set up mock for render method
        field.validate = mock.MagicMock(return_value=True)

        # Test render method
        result = field.render()
        self.assertEqual(result, ["option1", "option3"])
        self.assertEqual(field.value, ["option1", "option3"])
        mock_multi_select.assert_called_once_with("Select options", ["option1", "option2", "option3"], defaults=None)

    def test_form_init(self):
        """Test Form initialization."""
        form = Form(title="Test Form", description="Test description")
        self.assertEqual(form.title, "Test Form")
        self.assertEqual(form.description, "Test description")
        self.assertEqual(form.fields, [])

    def test_form_add_field(self):
        """Test Form add_field method."""
        form = Form()
        field = TextField("name", "Name")
        form.add_field(field)
        self.assertEqual(form.fields, [field])

    @mock.patch('hubqueue.ui.is_interactive', return_value=False)
    def test_form_render_non_interactive(self, mock_interactive):
        """Test Form render in non-interactive mode."""
        form = Form()
        field = TextField("name", "Name", default="default")
        form.add_field(field)

        result = form.render()
        self.assertEqual(result, {"name": "default"})

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.clear_screen')
    @mock.patch('hubqueue.ui.print_header')
    @mock.patch('hubqueue.ui.print_info')
    @mock.patch('hubqueue.ui.print_color')
    @mock.patch('hubqueue.ui.print_success')
    def test_form_render(self, mock_success, mock_color, mock_info, mock_header, mock_clear, mock_interactive):
        """Test Form render."""
        form = Form(title="Test Form", description="Test description")

        # Add fields with mocked render methods
        field1 = mock.MagicMock()
        field1.name = "field1"
        field1.render.return_value = "value1"

        field2 = mock.MagicMock()
        field2.name = "field2"
        field2.render.return_value = "value2"

        form.add_field(field1)
        form.add_field(field2)

        # Render form
        result = form.render()

        # Verify result
        self.assertEqual(result, {"field1": "value1", "field2": "value2"})

        # Verify method calls
        mock_clear.assert_called_once()
        mock_header.assert_called_once_with("Test Form")
        mock_info.assert_called_once_with("Test description")
        mock_success.assert_called_once_with("Test Form completed successfully!")
        field1.render.assert_called_once()
        field2.render.assert_called_once()

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.clear_screen')
    @mock.patch('hubqueue.ui.print_header')
    @mock.patch('hubqueue.ui.print_info')
    @mock.patch('hubqueue.ui.print_color')
    @mock.patch('hubqueue.ui.print_warning')
    def test_form_render_keyboard_interrupt(self, mock_warning, mock_color, mock_info, mock_header, mock_clear, mock_interactive):
        """Test Form render with KeyboardInterrupt."""
        form = Form(title="Test Form", description="Test description")

        # Add field with mocked render method that raises KeyboardInterrupt
        field = mock.MagicMock()
        field.name = "field"
        field.render.side_effect = KeyboardInterrupt()

        form.add_field(field)

        # Render form
        result = form.render()

        # Verify result
        self.assertIsNone(result)

        # Verify method calls
        mock_clear.assert_called_once()
        mock_header.assert_called_once_with("Test Form")
        mock_info.assert_called_once_with("Test description")
        mock_warning.assert_called_once_with("\nForm cancelled.")
        field.render.assert_called_once()

    def test_form_to_dict(self):
        """Test Form to_dict method."""
        form = Form(title="Test Form", description="Test description")

        # Add fields
        field1 = TextField("field1", "Field 1")
        field1.value = "value1"

        field2 = TextField("field2", "Field 2")
        field2.value = "value2"

        form.add_field(field1)
        form.add_field(field2)

        # Get form dictionary
        result = form.to_dict()

        # Verify result
        expected = {
            "title": "Test Form",
            "description": "Test description",
            "fields": [
                {
                    "name": "field1",
                    "label": "Field 1",
                    "required": False,
                    "default": None,
                    "help_text": None,
                    "value": "value1",
                },
                {
                    "name": "field2",
                    "label": "Field 2",
                    "required": False,
                    "default": None,
                    "help_text": None,
                    "value": "value2",
                },
            ],
        }

        self.assertEqual(result, expected)

    def test_repository_form(self):
        """Test RepositoryForm."""
        form = RepositoryForm()

        # Verify fields
        self.assertEqual(len(form.fields), 9)
        self.assertEqual(form.fields[0].name, "name")
        self.assertEqual(form.fields[1].name, "owner_type")
        self.assertEqual(form.fields[2].name, "owner")
        self.assertEqual(form.fields[3].name, "description")
        self.assertEqual(form.fields[4].name, "visibility")
        self.assertEqual(form.fields[5].name, "features")
        self.assertEqual(form.fields[6].name, "default_branch")
        self.assertEqual(form.fields[7].name, "create_readme")
        self.assertEqual(form.fields[8].name, "create_gitignore")

    def test_issue_form(self):
        """Test IssueForm."""
        # Test with repo_name
        form = IssueForm("owner/repo")

        # Verify fields
        self.assertEqual(len(form.fields), 6)
        self.assertEqual(form.fields[0].name, "title")
        self.assertEqual(form.fields[1].name, "type")
        self.assertEqual(form.fields[2].name, "priority")
        self.assertEqual(form.fields[3].name, "description")
        self.assertEqual(form.fields[4].name, "labels")
        self.assertEqual(form.fields[5].name, "add_assignees")

        # Test without repo_name
        form = IssueForm()

        # Verify fields
        self.assertEqual(len(form.fields), 7)
        self.assertEqual(form.fields[0].name, "repo_name")
        self.assertEqual(form.fields[1].name, "title")
        self.assertEqual(form.fields[2].name, "type")
        self.assertEqual(form.fields[3].name, "priority")
        self.assertEqual(form.fields[4].name, "description")
        self.assertEqual(form.fields[5].name, "labels")
        self.assertEqual(form.fields[6].name, "add_assignees")

    @mock.patch('hubqueue.ui.is_interactive', return_value=True)
    @mock.patch('hubqueue.ui.prompt')
    @mock.patch('hubqueue.ui.confirm')
    def test_issue_form_render(self, mock_confirm, mock_prompt, mock_interactive):
        """Test IssueForm render method."""
        # Mock UI functions
        mock_prompt.side_effect = ["owner/repo", "Test issue", "Issue description", "assignee1", "assignee2"]
        mock_confirm.side_effect = [True, True, False]

        # Create form with mocked field render methods
        form = IssueForm()

        # Mock field render methods
        for field in form.fields:
            field.render = mock.MagicMock(return_value=field.default)

        # Override repo_name field
        form.fields[0].render = mock.MagicMock(return_value="owner/repo")

        # Override add_assignees field
        form.fields[6].render = mock.MagicMock(return_value=True)

        # Mock Form.render to call our mocked field.render methods
        with mock.patch('hubqueue.forms.Form.render', return_value={"repo_name": "owner/repo", "add_assignees": True}):
            result = form.render()

        # Verify result
        self.assertEqual(result["repo_name"], "owner/repo")
        self.assertEqual(result["add_assignees"], True)

        # Mock the prompt and confirm calls for assignees
        mock_prompt.assert_any_call("Assignee username")
        mock_confirm.assert_any_call("Add another assignee?", default=False)

    def test_render_form(self):
        """Test render_form function."""
        form = mock.MagicMock()
        form.render.return_value = {"name": "value"}

        result = render_form(form)
        self.assertEqual(result, {"name": "value"})
        form.render.assert_called_once()

    def test_create_repository_form(self):
        """Test create_repository_form function."""
        form = create_repository_form()
        self.assertIsInstance(form, RepositoryForm)

    def test_create_issue_form(self):
        """Test create_issue_form function."""
        # Test with repo_name
        form = create_issue_form("owner/repo")
        self.assertIsInstance(form, IssueForm)
        self.assertEqual(form.repo_name, "owner/repo")

        # Test without repo_name
        form = create_issue_form()
        self.assertIsInstance(form, IssueForm)
        self.assertFalse(hasattr(form, "repo_name"))
