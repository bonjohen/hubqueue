"""
Tests for the templates module.
"""
import os
import json
import tempfile
import shutil
from unittest import TestCase, mock

from hubqueue.templates import (
    list_templates, get_template, create_template, delete_template,
    import_template_from_github, import_template_from_url,
    generate_project, list_template_variables
)


class TestTemplates(TestCase):
    """Test project templates and scaffolding functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_templates_empty(self):
        """Test listing templates when none exist."""
        # List templates
        templates = list_templates(self.templates_dir)
        
        # Verify result
        self.assertEqual(len(templates), 0)

    def test_list_templates(self):
        """Test listing templates."""
        # Create test templates
        template1_dir = os.path.join(self.templates_dir, "template1")
        os.makedirs(template1_dir, exist_ok=True)
        with open(os.path.join(template1_dir, "template.json"), "w") as f:
            json.dump({
                "name": "template1",
                "description": "Test Template 1",
                "version": "1.0.0",
                "variables": {}
            }, f)
        
        template2_dir = os.path.join(self.templates_dir, "template2")
        os.makedirs(template2_dir, exist_ok=True)
        with open(os.path.join(template2_dir, "template.json"), "w") as f:
            json.dump({
                "name": "template2",
                "description": "Test Template 2",
                "version": "2.0.0",
                "variables": {}
            }, f)
        
        # List templates
        templates = list_templates(self.templates_dir)
        
        # Verify result
        self.assertEqual(len(templates), 2)
        
        # Sort templates by name for consistent testing
        templates.sort(key=lambda t: t["name"])
        
        self.assertEqual(templates[0]["name"], "template1")
        self.assertEqual(templates[0]["description"], "Test Template 1")
        self.assertEqual(templates[0]["version"], "1.0.0")
        self.assertEqual(templates[0]["directory"], template1_dir)
        
        self.assertEqual(templates[1]["name"], "template2")
        self.assertEqual(templates[1]["description"], "Test Template 2")
        self.assertEqual(templates[1]["version"], "2.0.0")
        self.assertEqual(templates[1]["directory"], template2_dir)

    def test_get_template(self):
        """Test getting a template."""
        # Create test template
        template_dir = os.path.join(self.templates_dir, "template1")
        os.makedirs(template_dir, exist_ok=True)
        with open(os.path.join(template_dir, "template.json"), "w") as f:
            json.dump({
                "name": "template1",
                "description": "Test Template 1",
                "version": "1.0.0",
                "variables": {}
            }, f)
        
        # Get template
        template = get_template("template1", self.templates_dir)
        
        # Verify result
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "template1")
        self.assertEqual(template["description"], "Test Template 1")
        self.assertEqual(template["version"], "1.0.0")
        self.assertEqual(template["directory"], template_dir)

    def test_get_template_not_found(self):
        """Test getting a template that doesn't exist."""
        # Get template
        template = get_template("nonexistent", self.templates_dir)
        
        # Verify result
        self.assertIsNone(template)

    def test_create_template(self):
        """Test creating a template."""
        # Create source directory with files
        source_dir = os.path.join(self.temp_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        with open(os.path.join(source_dir, "file1.txt"), "w") as f:
            f.write("Test file 1")
        with open(os.path.join(source_dir, "file2.txt"), "w") as f:
            f.write("Test file 2")
        
        # Create template
        template = create_template(
            source_dir,
            "test-template",
            "Test Template",
            "1.0.0",
            {"var1": "value1"},
            self.templates_dir
        )
        
        # Verify result
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "test-template")
        self.assertEqual(template["description"], "Test Template")
        self.assertEqual(template["version"], "1.0.0")
        self.assertEqual(template["variables"], {"var1": "value1"})
        
        # Verify template directory
        template_dir = os.path.join(self.templates_dir, "test-template")
        self.assertTrue(os.path.isdir(template_dir))
        
        # Verify template.json
        with open(os.path.join(template_dir, "template.json"), "r") as f:
            template_json = json.load(f)
            self.assertEqual(template_json["name"], "test-template")
            self.assertEqual(template_json["description"], "Test Template")
            self.assertEqual(template_json["version"], "1.0.0")
            self.assertEqual(template_json["variables"], {"var1": "value1"})
        
        # Verify files
        self.assertTrue(os.path.isfile(os.path.join(template_dir, "file1.txt")))
        self.assertTrue(os.path.isfile(os.path.join(template_dir, "file2.txt")))
        
        with open(os.path.join(template_dir, "file1.txt"), "r") as f:
            self.assertEqual(f.read(), "Test file 1")
        with open(os.path.join(template_dir, "file2.txt"), "r") as f:
            self.assertEqual(f.read(), "Test file 2")

    def test_delete_template(self):
        """Test deleting a template."""
        # Create test template
        template_dir = os.path.join(self.templates_dir, "template1")
        os.makedirs(template_dir, exist_ok=True)
        with open(os.path.join(template_dir, "template.json"), "w") as f:
            json.dump({
                "name": "template1",
                "description": "Test Template 1",
                "version": "1.0.0",
                "variables": {}
            }, f)
        
        # Delete template
        result = delete_template("template1", self.templates_dir)
        
        # Verify result
        self.assertTrue(result)
        self.assertFalse(os.path.exists(template_dir))

    def test_delete_template_not_found(self):
        """Test deleting a template that doesn't exist."""
        # Delete template
        with self.assertRaises(Exception):
            delete_template("nonexistent", self.templates_dir)

    @mock.patch("hubqueue.templates.Github")
    @mock.patch("hubqueue.templates.requests.get")
    def test_import_template_from_github(self, mock_requests_get, mock_github):
        """Test importing a template from GitHub."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()
        mock_repo.description = "Test Repository"
        mock_repo.get_archive_link.return_value = "https://github.com/test-user/test-repo/archive/main.zip"
        
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Mock requests.get
        mock_response = mock.MagicMock()
        mock_response.content = b"test content"
        mock_requests_get.return_value = mock_response
        
        # Mock zipfile extraction
        with mock.patch("zipfile.ZipFile") as mock_zipfile:
            mock_zip = mock.MagicMock()
            mock_zipfile.return_value.__enter__.return_value = mock_zip
            
            # Mock os.listdir to return extracted directory
            with mock.patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["test-user-test-repo-abc123"]
                
                # Mock os.path.isdir to return True for extracted directory
                with mock.patch("os.path.isdir") as mock_isdir:
                    mock_isdir.return_value = True
                    
                    # Mock create_template
                    with mock.patch("hubqueue.templates.create_template") as mock_create_template:
                        mock_create_template.return_value = {
                            "name": "test-repo",
                            "description": "Test Repository",
                            "version": "1.0.0",
                            "directory": os.path.join(self.templates_dir, "test-repo")
                        }
                        
                        # Import template
                        template = import_template_from_github(
                            "test-user/test-repo",
                            None,
                            None,
                            "test-token",
                            self.templates_dir
                        )
                        
                        # Verify result
                        self.assertIsNotNone(template)
                        self.assertEqual(template["name"], "test-repo")
                        self.assertEqual(template["description"], "Test Repository")
                        self.assertEqual(template["version"], "1.0.0")
                        
                        # Verify API calls
                        mock_github.assert_called_once_with("test-token")
                        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
                        mock_repo.get_archive_link.assert_called_once_with("zipball")
                        mock_requests_get.assert_called_once_with("https://github.com/test-user/test-repo/archive/main.zip")
                        mock_zipfile.assert_called_once()
                        mock_zip.extractall.assert_called_once()
                        mock_create_template.assert_called_once()

    @mock.patch("hubqueue.templates.requests.get")
    def test_import_template_from_url(self, mock_requests_get):
        """Test importing a template from a URL."""
        # Mock requests.get
        mock_response = mock.MagicMock()
        mock_response.content = b"test content"
        mock_requests_get.return_value = mock_response
        
        # Mock zipfile extraction
        with mock.patch("zipfile.ZipFile") as mock_zipfile:
            mock_zip = mock.MagicMock()
            mock_zipfile.return_value.__enter__.return_value = mock_zip
            
            # Mock create_template
            with mock.patch("hubqueue.templates.create_template") as mock_create_template:
                mock_create_template.return_value = {
                    "name": "test-template",
                    "description": "Template imported from https://example.com/template.zip",
                    "version": "1.0.0",
                    "directory": os.path.join(self.templates_dir, "test-template")
                }
                
                # Import template
                template = import_template_from_url(
                    "https://example.com/template.zip",
                    "test-template",
                    None,
                    self.templates_dir
                )
                
                # Verify result
                self.assertIsNotNone(template)
                self.assertEqual(template["name"], "test-template")
                self.assertEqual(template["description"], "Template imported from https://example.com/template.zip")
                self.assertEqual(template["version"], "1.0.0")
                
                # Verify API calls
                mock_requests_get.assert_called_once_with("https://example.com/template.zip")
                mock_zipfile.assert_called_once()
                mock_zip.extractall.assert_called_once()
                mock_create_template.assert_called_once()

    def test_generate_project(self):
        """Test generating a project from a template."""
        # Create test template
        template_dir = os.path.join(self.templates_dir, "test-template")
        os.makedirs(template_dir, exist_ok=True)
        
        # Create template.json
        with open(os.path.join(template_dir, "template.json"), "w") as f:
            json.dump({
                "name": "test-template",
                "description": "Test Template",
                "version": "1.0.0",
                "variables": {
                    "project_name": {
                        "description": "Project name",
                        "default": "my-project"
                    },
                    "author": {
                        "description": "Author name",
                        "default": "John Doe"
                    }
                }
            }, f)
        
        # Create template files
        with open(os.path.join(template_dir, "README.md"), "w") as f:
            f.write("# {{ project_name }}\n\nCreated by {{ author }}")
        
        with open(os.path.join(template_dir, "{{ project_name }}.py"), "w") as f:
            f.write("# {{ project_name }} by {{ author }}\n\nprint('Hello, {{ project_name }}!')")
        
        # Create output directory
        output_dir = os.path.join(self.temp_dir, "output")
        
        # Generate project
        result = generate_project(
            "test-template",
            output_dir,
            {"project_name": "awesome-project", "author": "Jane Smith"},
            self.templates_dir
        )
        
        # Verify result
        self.assertEqual(result, output_dir)
        
        # Verify generated files
        self.assertTrue(os.path.isfile(os.path.join(output_dir, "README.md")))
        self.assertTrue(os.path.isfile(os.path.join(output_dir, "awesome-project.py")))
        
        # Verify file contents
        with open(os.path.join(output_dir, "README.md"), "r") as f:
            self.assertEqual(f.read(), "# awesome-project\n\nCreated by Jane Smith")
        
        with open(os.path.join(output_dir, "awesome-project.py"), "r") as f:
            self.assertEqual(f.read(), "# awesome-project by Jane Smith\n\nprint('Hello, awesome-project!')")

    def test_list_template_variables(self):
        """Test listing template variables."""
        # Create test template
        template_dir = os.path.join(self.templates_dir, "test-template")
        os.makedirs(template_dir, exist_ok=True)
        
        # Create template.json
        with open(os.path.join(template_dir, "template.json"), "w") as f:
            json.dump({
                "name": "test-template",
                "description": "Test Template",
                "version": "1.0.0",
                "variables": {
                    "project_name": {
                        "description": "Project name",
                        "default": "my-project"
                    },
                    "author": {
                        "description": "Author name",
                        "default": "John Doe"
                    }
                }
            }, f)
        
        # List template variables
        variables = list_template_variables("test-template", self.templates_dir)
        
        # Verify result
        self.assertIsNotNone(variables)
        self.assertEqual(len(variables), 2)
        self.assertIn("project_name", variables)
        self.assertIn("author", variables)
        self.assertEqual(variables["project_name"]["description"], "Project name")
        self.assertEqual(variables["project_name"]["default"], "my-project")
        self.assertEqual(variables["author"]["description"], "Author name")
        self.assertEqual(variables["author"]["default"], "John Doe")
