"""
Project templates and scaffolding module for HubQueue.
"""
import os
import json
import shutil
import zipfile
import tempfile
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()

# Default templates directory
DEFAULT_TEMPLATES_DIR = os.path.join(os.path.expanduser("~"), ".hubqueue", "templates")


def list_templates(templates_dir=None):
    """
    List available project templates.

    Args:
        templates_dir (str, optional): Directory containing templates. If None, uses default.

    Returns:
        list: List of template dictionaries
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Create templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)

    templates = []

    # List directories in templates directory
    for item in os.listdir(templates_dir):
        template_dir = os.path.join(templates_dir, item)

        # Skip non-directories
        if not os.path.isdir(template_dir):
            continue

        # Check for template.json file
        template_json = os.path.join(template_dir, "template.json")
        if os.path.isfile(template_json):
            try:
                with open(template_json, "r", encoding="utf-8") as f:
                    template_info = json.load(f)

                    # Add template directory
                    template_info["directory"] = template_dir

                    # Add to list
                    templates.append(template_info)
            except Exception as e:
                logger.warning(f"Error loading template {item}: {str(e)}")
        else:
            # Create basic template info
            templates.append({
                "name": item,
                "description": f"Template directory: {item}",
                "version": "unknown",
                "directory": template_dir
            })

    logger.info(f"Found {len(templates)} templates in {templates_dir}")
    return templates


def get_template(template_name, templates_dir=None):
    """
    Get information about a specific template.

    Args:
        template_name (str): Template name
        templates_dir (str, optional): Directory containing templates. If None, uses default.

    Returns:
        dict: Template information or None if not found
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Get all templates
    templates = list_templates(templates_dir)

    # Find template by name
    for template in templates:
        if template["name"] == template_name:
            return template

    logger.warning(f"Template {template_name} not found in {templates_dir}")
    return None


def create_template(template_dir, name, description, version="1.0.0", variables=None, templates_dir=None):
    """
    Create a new template from a directory.

    Args:
        template_dir (str): Directory containing template files
        name (str): Template name
        description (str): Template description
        version (str, optional): Template version. Defaults to "1.0.0".
        variables (dict, optional): Template variables. Defaults to None.
        templates_dir (str, optional): Directory to save template to. If None, uses default.

    Returns:
        dict: Template information or None if creation failed
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Create templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)

    # Create template directory
    template_path = os.path.join(templates_dir, name)

    # Check if template already exists
    if os.path.exists(template_path):
        logger.error(f"Template {name} already exists in {templates_dir}")
        raise FileExistsError(f"Template {name} already exists")

    try:
        # Create template directory
        os.makedirs(template_path, exist_ok=True)

        # Copy template files
        for item in os.listdir(template_dir):
            source = os.path.join(template_dir, item)
            destination = os.path.join(template_path, item)

            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

        # Create template.json file
        template_info = {
            "name": name,
            "description": description,
            "version": version,
            "variables": variables or {},
        }

        with open(os.path.join(template_path, "template.json"), "w", encoding="utf-8") as f:
            json.dump(template_info, f, indent=2)

        # Add template directory
        template_info["directory"] = template_path

        logger.info(f"Created template {name} in {templates_dir}")
        return template_info
    except Exception as e:
        # Clean up if creation failed
        if os.path.exists(template_path):
            shutil.rmtree(template_path)

        logger.error(f"Error creating template: {str(e)}")
        raise Exception(f"Error creating template: {str(e)}")


def delete_template(template_name, templates_dir=None):
    """
    Delete a template.

    Args:
        template_name (str): Template name
        templates_dir (str, optional): Directory containing templates. If None, uses default.

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Get template
    template = get_template(template_name, templates_dir)
    if not template:
        logger.error(f"Template {template_name} not found in {templates_dir}")
        raise FileNotFoundError(f"Template {template_name} not found")

    try:
        # Delete template directory
        shutil.rmtree(template["directory"])

        logger.info(f"Deleted template {template_name} from {templates_dir}")
        return True
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise Exception(f"Error deleting template: {str(e)}")


def import_template_from_github(repo_name, path=None, name=None, token=None, templates_dir=None):
    """
    Import a template from a GitHub repository.

    Args:
        repo_name (str): Repository name in format 'owner/repo'
        path (str, optional): Path within repository to use as template. If None, uses root.
        name (str, optional): Template name. If None, uses repository name.
        token (str, optional): GitHub token. If None, will try to get from config.
        templates_dir (str, optional): Directory to save template to. If None, uses default.

    Returns:
        dict: Template information or None if import failed
    """
    token = token or get_github_token()
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Create templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)

    # Use repository name as template name if not provided
    if not name:
        name = repo_name.split("/")[-1]

    try:
        logger.debug(f"Importing template from GitHub repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download repository as zip
            zip_url = repo.get_archive_link("zipball")
            response = requests.get(zip_url)
            response.raise_for_status()

            # Save zip file
            zip_path = os.path.join(temp_dir, "repo.zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)

            # Extract zip file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find extracted directory
            extracted_dir = None
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path) and item != "__MACOSX":
                    extracted_dir = item_path
                    break

            if not extracted_dir:
                logger.error(f"No directory found in extracted zip from {repo_name}")
                raise Exception(f"No directory found in extracted zip from {repo_name}")

            # Use specified path within repository
            if path:
                template_source = os.path.join(extracted_dir, path)
                if not os.path.exists(template_source):
                    logger.error(f"Path {path} not found in repository {repo_name}")
                    raise Exception(f"Path {path} not found in repository {repo_name}")
            else:
                template_source = extracted_dir

            # Get repository description
            description = repo.description or f"Template imported from {repo_name}"

            # Create template
            return create_template(
                template_source,
                name,
                description,
                "1.0.0",
                None,
                templates_dir
            )
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error importing template from GitHub: {str(e)}")
        raise Exception(f"Error importing template from GitHub: {str(e)}")


def import_template_from_url(url, name, description=None, templates_dir=None):
    """
    Import a template from a URL.

    Args:
        url (str): URL to zip file containing template
        name (str): Template name
        description (str, optional): Template description. If None, uses URL.
        templates_dir (str, optional): Directory to save template to. If None, uses default.

    Returns:
        dict: Template information or None if import failed
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Create templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)

    # Use URL as description if not provided
    if not description:
        description = f"Template imported from {url}"

    try:
        logger.debug(f"Importing template from URL {url}")

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download zip file
            response = requests.get(url)
            response.raise_for_status()

            # Save zip file
            zip_path = os.path.join(temp_dir, "template.zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)

            # Extract zip file
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Create template
            return create_template(
                extract_dir,
                name,
                description,
                "1.0.0",
                None,
                templates_dir
            )
    except Exception as e:
        logger.error(f"Error importing template from URL: {str(e)}")
        raise Exception(f"Error importing template from URL: {str(e)}")


def generate_project(template_name, output_dir, variables=None, templates_dir=None):
    """
    Generate a project from a template.

    Args:
        template_name (str): Template name
        output_dir (str): Output directory
        variables (dict, optional): Template variables. Defaults to None.
        templates_dir (str, optional): Directory containing templates. If None, uses default.

    Returns:
        str: Output directory or None if generation failed
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR
    variables = variables or {}

    # Get template
    template = get_template(template_name, templates_dir)
    if not template:
        logger.error(f"Template {template_name} not found in {templates_dir}")
        raise FileNotFoundError(f"Template {template_name} not found")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Load template variables from template.json
        template_json_path = os.path.join(template["directory"], "template.json")
        template_variables = {}

        if os.path.isfile(template_json_path):
            with open(template_json_path, "r", encoding="utf-8") as f:
                template_info = json.load(f)
                template_variables = template_info.get("variables", {})

        # Merge template variables with provided variables
        merged_variables = {**template_variables, **variables}

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(template["directory"]))

        # Process template files
        for root, dirs, files in os.walk(template["directory"]):
            # Skip template.json file
            if "template.json" in files:
                files.remove("template.json")

            # Calculate relative path
            rel_path = os.path.relpath(root, template["directory"])
            if rel_path == ".":
                rel_path = ""

            # Create directories
            for dir_name in dirs:
                # Process directory name with Jinja2
                dir_template = Template(dir_name)
                processed_dir_name = dir_template.render(**merged_variables)

                # Create directory
                dir_path = os.path.join(output_dir, rel_path, processed_dir_name)
                os.makedirs(dir_path, exist_ok=True)

            # Process files
            for file_name in files:
                # Skip template.json file
                if file_name == "template.json":
                    continue

                # Process file name with Jinja2
                file_template = Template(file_name)
                processed_file_name = file_template.render(**merged_variables)

                # Read file content
                file_path = os.path.join(root, file_name)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Process file content with Jinja2
                content_template = Template(content)
                processed_content = content_template.render(**merged_variables)

                # Write processed file
                output_file_path = os.path.join(output_dir, rel_path, processed_file_name)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(processed_content)

        logger.info(f"Generated project from template {template_name} in {output_dir}")
        return output_dir
    except Exception as e:
        logger.error(f"Error generating project from template: {str(e)}")
        raise Exception(f"Error generating project from template: {str(e)}")


def list_template_variables(template_name, templates_dir=None):
    """
    List variables for a template.

    Args:
        template_name (str): Template name
        templates_dir (str, optional): Directory containing templates. If None, uses default.

    Returns:
        dict: Template variables or None if template not found
    """
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR

    # Get template
    template = get_template(template_name, templates_dir)
    if not template:
        logger.error(f"Template {template_name} not found in {templates_dir}")
        return None

    # Load template variables from template.json
    template_json_path = os.path.join(template["directory"], "template.json")
    if os.path.isfile(template_json_path):
        try:
            with open(template_json_path, "r", encoding="utf-8") as f:
                template_info = json.load(f)
                return template_info.get("variables", {})
        except Exception as e:
            logger.error(f"Error loading template variables: {str(e)}")
            raise Exception(f"Error loading template variables: {str(e)}")

    return {}
