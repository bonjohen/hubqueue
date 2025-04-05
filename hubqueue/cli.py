"""
Command-line interface for HubQueue.
"""
import os
import json
import click
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from tabulate import tabulate
from . import __version__
from .auth import (
    get_github_token, validate_token, save_token,
    clear_token, get_user_info, start_oauth_flow,
    complete_oauth_flow
)
from .config import (
    get_preference, set_preference, list_preferences,
    get_editor, get_default_repo, set_default_repo
)
from .repository import (
    create_repository, clone_repository, init_repository,
    create_project_directories, generate_gitignore, generate_readme,
    generate_license, create_branch, stage_and_commit, push_commits,
    create_pull_request, fork_repository, manage_collaborators
)
from .issues import (
    create_issue, checkout_pull_request,
    get_issue, get_pull_request
)
from .release import (
    update_version, create_tag, push_tag,
    generate_release_notes, create_github_release,
    upload_release_asset
)
from .workflow import (
    list_workflows, trigger_workflow, list_workflow_runs,
    get_workflow_run, monitor_workflow_run, cancel_workflow_run,
    rerun_workflow_run, list_repository_secrets, create_repository_secret,
    delete_repository_secret, list_workflow_caches, delete_workflow_cache
)
from .gist import (
    list_gists, get_gist, create_gist, update_gist, delete_gist,
    star_gist, unstar_gist, is_gist_starred, add_gist_comment,
    delete_gist_comment, fork_gist, download_gist, upload_gist
)
from .templates import (
    list_templates, get_template, create_template, delete_template,
    import_template_from_github, import_template_from_url,
    generate_project, list_template_variables
)
from .projects import (
    list_project_boards, get_project_board, create_project_board,
    create_project_column, add_issue_to_project, add_pr_to_project,
    add_note_to_project, move_project_card, delete_project_card,
    delete_project_column, delete_project_board, create_project_from_template,
    configure_project_automation
)
from .system import (
    get_system_info, check_command_availability, check_git_config,
    set_git_config, check_dependencies, install_dependency,
    check_windows_compatibility, setup_windows_environment,
    setup_unix_environment, setup_environment, export_environment,
    check_for_updates, update_hubqueue
)
from .logging import get_logger, setup_logging

# Get logger
logger = get_logger()

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version=__version__)
@click.option("--log-level", type=click.Choice(["debug", "info", "warning", "error", "critical"]),
              default="info", help="Set the logging level")
@click.option("--log-file", help="Log to this file")
def main(log_level, log_file):
    """HubQueue - A command-line interface for GitHub tools."""
    # Set up logging
    setup_logging(level=log_level, log_file=log_file)
    logger.debug(f"HubQueue started with log level: {log_level}")


# Authentication commands group
@main.group()
def auth():
    """Authentication commands for GitHub."""
    pass


@auth.command()
@click.option("--token", prompt=True, hide_input=True, help="GitHub API token")
def login(token):
    """Login with GitHub token."""
    logger.debug("Attempting to login with token")
    if validate_token(token):
        save_token(token)
        user_info = get_user_info(token)
        logger.info(f"Successfully logged in as {user_info['login']}")
        click.echo(f"Successfully logged in as {user_info['login']}")
    else:
        logger.error("Invalid GitHub token provided")
        click.echo("Error: Invalid GitHub token")


@auth.command()
def logout():
    """Logout and remove stored GitHub token."""
    logger.debug("Attempting to logout")
    if clear_token():
        logger.info("Successfully logged out")
        click.echo("Successfully logged out")
    else:
        logger.warning("No token found when attempting to logout")
        click.echo("No token found")


@auth.command()
def status():
    """Check authentication status."""
    logger.debug("Checking authentication status")
    token = get_github_token()
    if not token:
        logger.info("Not logged in")
        click.echo("Not logged in")
        return

    if validate_token(token):
        user_info = get_user_info(token)
        logger.info(f"Logged in as {user_info['login']}")
        click.echo(f"Logged in as {user_info['login']}")

        # Display user information in a table
        table_data = [
            ["Username", user_info["login"]],
            ["Name", user_info["name"] or "N/A"],
            ["Email", user_info["email"] or "N/A"],
            ["Public Repos", user_info["public_repos"]],
            ["Private Repos", user_info["private_repos"]],
            ["Profile URL", user_info["html_url"]],
        ]
        click.echo(tabulate(table_data, tablefmt="simple"))
    else:
        logger.warning("Token is invalid")
        click.echo("Token is invalid. Please login again.")


@auth.command()
@click.option("--client-id", required=True, help="GitHub OAuth client ID")
@click.option("--client-secret", required=True, help="GitHub OAuth client secret")
def oauth(client_id, client_secret):
    """Login with GitHub OAuth."""
    auth_url = start_oauth_flow(client_id)
    click.echo(f"Opening browser to authorize application...")
    click.echo(f"If the browser doesn't open, visit this URL: {auth_url}")

    # Open browser for authorization
    webbrowser.open(auth_url)

    # Get authorization code from user
    code = click.prompt("Enter the authorization code from the browser")

    # Complete OAuth flow
    token = complete_oauth_flow(code, client_id, client_secret)
    if token:
        user_info = get_user_info(token)
        click.echo(f"Successfully logged in as {user_info['login']}")
    else:
        click.echo("Error: Failed to complete OAuth flow")


# Configuration commands group
@main.group()
def config():
    """Configuration commands for HubQueue."""
    pass


@config.command("list")
def list_config():
    """List all configuration settings."""
    preferences = list_preferences()
    if not preferences:
        click.echo("No preferences set")
        return

    # Display preferences in a table
    table_data = [[key, value] for key, value in preferences.items()]
    click.echo(tabulate(table_data, headers=["Setting", "Value"], tablefmt="simple"))


@config.command()
@click.argument("key")
def get(key):
    """Get a configuration setting."""
    value = get_preference(key)
    if value is None:
        click.echo(f"No preference set for '{key}'")
    else:
        click.echo(f"{key} = {value}")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a configuration setting."""
    # Convert string values to appropriate types
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    elif value.isdigit():
        value = int(value)

    if set_preference(key, value):
        click.echo(f"Set {key} = {value}")
    else:
        click.echo(f"Failed to set {key}")


@config.command()
@click.argument("editor")
def set_editor(editor):
    """Set the default text editor."""
    if set_preference("editor", editor):
        click.echo(f"Set default editor to {editor}")
    else:
        click.echo("Failed to set default editor")


@config.command()
def get_editor_cmd():
    """Get the default text editor."""
    editor = get_editor()
    click.echo(f"Default editor: {editor}")


@config.command()
@click.argument("repo")
def set_repo(repo):
    """Set the default repository (format: owner/repo)."""
    if "/" not in repo:
        click.echo("Error: Repository must be in format 'owner/repo'")
        return

    if set_default_repo(repo):
        click.echo(f"Set default repository to {repo}")
    else:
        click.echo("Failed to set default repository")


@config.command()
def get_repo():
    """Get the default repository."""
    repo = get_default_repo()
    if repo:
        click.echo(f"Default repository: {repo}")
    else:
        click.echo("No default repository set")


# Repository management commands group
@main.group()
def repo():
    """Repository management commands."""
    pass


@repo.command()
@click.argument("name")
@click.option("--description", help="Repository description")
@click.option("--private/--public", default=False, help="Whether the repository is private")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def create(name, description, private, token):
    """Create a new repository on GitHub."""
    logger.debug(f"Creating repository: {name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        repo_info = create_repository(name, description, private, token)
        logger.info(f"Repository created successfully: {repo_info['html_url']}")
        click.echo(f"Repository created successfully: {repo_info['html_url']}")
        click.echo("\nClone with HTTPS:")
        click.echo(f"  git clone {repo_info['clone_url']}")
        click.echo("\nClone with SSH:")
        click.echo(f"  git clone {repo_info['ssh_url']}")
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("url")
@click.option("--directory", help="Directory to clone into")
@click.option("--token", help="GitHub API token for private repos (or set GITHUB_TOKEN env variable)")
def clone(url, directory, token):
    """Clone a repository to the local machine."""
    token = token or get_github_token()

    try:
        repo_path = clone_repository(url, directory, token)
        click.echo(f"Repository cloned successfully to {repo_path}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.option("--directory", default=".", help="Directory to initialize")
def init(directory):
    """Initialize a Git repository in a specified directory."""
    try:
        init_repository(directory)
        click.echo(f"Git repository initialized in {directory}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.option("--directory", default=".", help="Base directory")
@click.option("--dirs", multiple=True, help="Directories to create (can be specified multiple times)")
def create_dirs(directory, dirs):
    """Create essential project directories."""
    try:
        dirs_list = list(dirs) if dirs else None
        created_dirs = create_project_directories(directory, dirs_list)
        if created_dirs:
            click.echo("Created directories:")
            for dir_path in created_dirs:
                click.echo(f"  {dir_path}")
        else:
            click.echo("No directories created (they may already exist)")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.option("--directory", default=".", help="Directory to create files in")
@click.option("--name", help="Project name (defaults to directory name)")
@click.option("--description", help="Project description")
@click.option("--license", default="MIT", help="License type (default: MIT)")
@click.option("--author", help="Author name for license")
@click.option("--gitignore", default="Python", help="Gitignore template (default: Python)")
def scaffold(directory, name, description, license, author, gitignore):
    """Generate standard project files (README.md, .gitignore, LICENSE)."""
    try:
        # Create directory if it doesn't exist
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            click.echo(f"Created directory: {directory}")

        # Generate README.md
        try:
            readme_path = generate_readme(directory, name, description)
            click.echo(f"Created README.md: {readme_path}")
        except Exception as e:
            click.echo(f"Error creating README.md: {str(e)}")

        # Generate .gitignore
        try:
            gitignore_path = generate_gitignore(directory, gitignore)
            click.echo(f"Created .gitignore: {gitignore_path}")
        except Exception as e:
            click.echo(f"Error creating .gitignore: {str(e)}")

        # Generate LICENSE
        try:
            license_path = generate_license(directory, license, author)
            click.echo(f"Created LICENSE: {license_path}")
        except Exception as e:
            click.echo(f"Error creating LICENSE: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("branch_name")
@click.option("--base", default="main", help="Base branch to create from (default: main)")
@click.option("--directory", default=".", help="Repository directory")
def branch(branch_name, base, directory):
    """Create and switch to a new feature branch."""
    try:
        created_branch = create_branch(branch_name, base, directory)
        click.echo(f"Created and switched to branch: {created_branch}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("message")
@click.option("--directory", default=".", help="Repository directory")
@click.option("--files", multiple=True, help="Files to stage (can be specified multiple times)")
def commit(message, directory, files):
    """Stage and commit changes to the repository."""
    try:
        files_list = list(files) if files else None
        commit_hash = stage_and_commit(message, directory, files_list)
        click.echo(f"Changes committed successfully: {commit_hash}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option("--branch", help="Branch to push (default: current branch)")
@click.option("--directory", default=".", help="Repository directory")
def push(remote, branch, directory):
    """Push commits to the remote repository."""
    try:
        push_commits(remote, branch, directory)
        branch_name = branch or "current branch"
        click.echo(f"Commits pushed successfully to {remote}/{branch_name}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("title")
@click.option("--body", help="Pull request description")
@click.option("--base", default="main", help="Base branch for PR (default: main)")
@click.option("--head", help="Head branch for PR (default: current branch)")
@click.option("--repo", help="Repository name in format 'owner/repo'")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def pr(title, body, base, head, repo, token):
    """Create a pull request from the current branch to the main branch."""
    token = token or get_github_token()
    if not token:
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        pr_info = create_pull_request(title, body, base, head, repo, token)
        click.echo(f"Pull request created successfully: {pr_info['html_url']}")
        click.echo(f"PR #{pr_info['number']}: {pr_info['title']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("repo_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def fork(repo_name, token):
    """Fork an existing repository to your GitHub account."""
    token = token or get_github_token()
    if not token:
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        fork_info = fork_repository(repo_name, token)
        click.echo(f"Repository forked successfully: {fork_info['html_url']}")
        click.echo("\nClone with HTTPS:")
        click.echo(f"  git clone {fork_info['clone_url']}")
        click.echo("\nClone with SSH:")
        click.echo(f"  git clone {fork_info['ssh_url']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@repo.command()
@click.argument("repo_name")
@click.argument("username")
@click.option("--permission", type=click.Choice(["pull", "push", "admin"]), default="push",
              help="Permission level (default: push)")
@click.option("--remove", is_flag=True, help="Remove collaborator instead of adding")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def collaborator(repo_name, username, permission, remove, token):
    """Manage repository collaborators and permissions."""
    logger.debug(f"Managing collaborator {username} for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Determine if adding or removing collaborator
        operation = "Removing" if remove else "Adding"
        logger.debug(f"{operation} collaborator {username} to/from {repo_name}")

        manage_collaborators(repo_name, username, permission, not remove, token)
        if remove:
            logger.info(f"Collaborator {username} removed from {repo_name}")
            click.echo(f"Collaborator {username} removed from {repo_name}")
        else:
            logger.info(f"Collaborator {username} added to {repo_name} with {permission} permission")
            click.echo(f"Collaborator {username} added to {repo_name} with {permission} permission")
    except Exception as e:
        logger.error(f"Error managing collaborator: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.option("--repo", help="Repository name in format 'owner/repo'")
@click.option("--state", type=click.Choice(["open", "closed", "all"]), default="open",
              help="Issue state (default: open)")
@click.option("--label", multiple=True, help="Filter by label (can be specified multiple times)")
@click.option("--assignee", help="Filter by assignee username")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--format", type=click.Choice(["table", "simple"]), default="simple",
              help="Output format (default: simple)")
def list_issues(repo, state, label, assignee, token, format):
    """List issues for a repository."""
    logger.debug(f"Listing issues for repository {repo}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not repo:
        logger.error("Repository not specified")
        click.echo("Error: Repository not specified. Use --repo option.")
        return

    try:
        # Convert labels to list if provided
        labels = list(label) if label else None

        # Get issues
        from .issues import list_issues as get_issues
        issues = get_issues(repo, state, labels, assignee, token)

        if not issues:
            logger.info(f"No {state} issues found for {repo}")
            click.echo(f"No {state} issues found for {repo}")
            return

        # Display issues
        if format == "table":
            # Create table data
            headers = ["Number", "Title", "State", "Assignees", "Labels"]
            table_data = [
                [
                    f"#{issue['number']}",
                    issue['title'],
                    issue['state'],
                    ", ".join(issue['assignees']) if issue['assignees'] else "None",
                    ", ".join(issue['labels']) if issue['labels'] else "None"
                ] for issue in issues
            ]
            click.echo(f"{state.capitalize()} issues for {repo}:")
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Simple format
            click.echo(f"{state.capitalize()} issues for {repo}:")
            for issue in issues:
                click.echo(f"#{issue['number']} - {issue['title']}")
    except Exception as e:
        logger.error(f"Error listing issues: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.option("--repo", help="Repository name in format 'owner/repo'")
@click.option("--state", type=click.Choice(["open", "closed", "all"]), default="open",
              help="Pull request state (default: open)")
@click.option("--base", help="Filter by base branch name")
@click.option("--head", help="Filter by head branch name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--format", type=click.Choice(["table", "simple"]), default="simple",
              help="Output format (default: simple)")
def list_prs(repo, state, base, head, token, format):
    """List pull requests for a repository."""
    logger.debug(f"Listing pull requests for repository {repo}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not repo:
        logger.error("Repository not specified")
        click.echo("Error: Repository not specified. Use --repo option.")
        return

    try:
        # Get pull requests
        from .issues import list_pull_requests as get_pull_requests
        prs = get_pull_requests(repo, state, base, head, token)

        if not prs:
            logger.info(f"No {state} pull requests found for {repo}")
            click.echo(f"No {state} pull requests found for {repo}")
            return

        # Display pull requests
        if format == "table":
            # Create table data
            headers = ["Number", "Title", "State", "Base → Head", "User"]
            table_data = [
                [
                    f"#{pr['number']}",
                    pr['title'],
                    pr['state'],
                    f"{pr['base']} → {pr['head']}",
                    pr['user']
                ] for pr in prs
            ]
            click.echo(f"{state.capitalize()} pull requests for {repo}:")
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Simple format
            click.echo(f"{state.capitalize()} pull requests for {repo}:")
            for pr in prs:
                click.echo(f"#{pr['number']} - {pr['title']}")
    except Exception as e:
        logger.error(f"Error listing pull requests: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.argument("repo_name")
@click.argument("title")
@click.option("--body", help="Issue body")
@click.option("--label", multiple=True, help="Label to apply (can be specified multiple times)")
@click.option("--assignee", multiple=True, help="Username to assign (can be specified multiple times)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def create_issue_cmd(repo_name, title, body, label, assignee, token):
    """Create a new issue in a repository."""
    logger.debug(f"Creating issue in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Convert labels and assignees to lists if provided
        labels = list(label) if label else None
        assignees = list(assignee) if assignee else None

        # Create issue
        issue = create_issue(repo_name, title, body, labels, assignees, token)

        logger.info(f"Created issue #{issue['number']} in {repo_name}")
        click.echo(f"Created issue #{issue['number']}: {issue['title']}")
        click.echo(f"URL: {issue['html_url']}")
    except Exception as e:
        logger.error(f"Error creating issue: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.argument("repo_name")
@click.argument("pr_number", type=int)
@click.option("--directory", default=".", help="Repository directory (default: current directory)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def checkout_pr(repo_name, pr_number, directory, token):
    """Checkout a pull request locally for review."""
    logger.debug(f"Checking out pull request #{pr_number} from {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Checkout pull request
        pr_info = checkout_pull_request(repo_name, pr_number, directory, token)

        logger.info(f"Checked out pull request #{pr_number} to branch {pr_info['branch']}")
        click.echo(f"Checked out pull request #{pr_number}: {pr_info['title']}")
        click.echo(f"Branch: {pr_info['branch']}")
        click.echo(f"Base: {pr_info['base']}")
        click.echo(f"Head: {pr_info['head']}")
        click.echo(f"URL: {pr_info['html_url']}")
    except Exception as e:
        logger.error(f"Error checking out pull request: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.argument("repo_name")
@click.argument("issue_number", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def view_issue(repo_name, issue_number, token):
    """View detailed information about an issue."""
    logger.debug(f"Viewing issue #{issue_number} from {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Get issue
        issue = get_issue(repo_name, issue_number, token)

        # Display issue information
        click.echo(f"Issue #{issue['number']}: {issue['title']}")
        click.echo(f"State: {issue['state']}")
        click.echo(f"Created by: {issue['user']}")
        click.echo(f"Created at: {issue['created_at']}")
        click.echo(f"Updated at: {issue['updated_at']}")
        click.echo(f"URL: {issue['html_url']}")

        if issue['assignees']:
            click.echo(f"Assignees: {', '.join(issue['assignees'])}")
        else:
            click.echo("Assignees: None")

        if issue['labels']:
            click.echo(f"Labels: {', '.join(issue['labels'])}")
        else:
            click.echo("Labels: None")

        click.echo("\nDescription:")
        click.echo(issue['body'] or "(No description)")

        if issue['comments']:
            click.echo(f"\nComments ({len(issue['comments'])}):\n")
            for i, comment in enumerate(issue['comments'], 1):
                click.echo(f"Comment #{i} by {comment['user']} on {comment['created_at']}:")
                click.echo(f"{comment['body']}\n")
    except Exception as e:
        logger.error(f"Error viewing issue: {str(e)}")
        click.echo(f"Error: {str(e)}")


@main.command()
@click.argument("repo_name")
@click.argument("pr_number", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def view_pr(repo_name, pr_number, token):
    """View detailed information about a pull request."""
    logger.debug(f"Viewing pull request #{pr_number} from {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Get pull request
        pr = get_pull_request(repo_name, pr_number, token)

        # Display pull request information
        click.echo(f"Pull Request #{pr['number']}: {pr['title']}")
        click.echo(f"State: {pr['state']}")
        click.echo(f"Created by: {pr['user']}")
        click.echo(f"Created at: {pr['created_at']}")
        click.echo(f"Updated at: {pr['updated_at']}")
        click.echo(f"URL: {pr['html_url']}")
        click.echo(f"Branch: {pr['head']} → {pr['base']}")

        if pr['merged']:
            click.echo("Status: Merged")
        elif pr['mergeable'] is True:
            click.echo("Status: Ready to merge")
        elif pr['mergeable'] is False:
            click.echo("Status: Conflicts need to be resolved")
        else:
            click.echo("Status: Unknown")

        click.echo(f"Changes: +{pr['additions']} -{pr['deletions']} in {pr['changed_files']} files")

        click.echo("\nDescription:")
        click.echo(pr['body'] or "(No description)")

        if pr['commits']:
            click.echo(f"\nCommits ({len(pr['commits'])}):\n")
            for i, commit in enumerate(pr['commits'], 1):
                click.echo(f"Commit {i}: {commit['sha'][:7]} by {commit['author']} on {commit['date']}")
                click.echo(f"  {commit['message'].split('\n')[0]}")

        if pr['comments']:
            click.echo(f"\nComments ({len(pr['comments'])}):\n")
            for i, comment in enumerate(pr['comments'], 1):
                click.echo(f"Comment #{i} by {comment['user']} on {comment['created_at']}:")
                click.echo(f"{comment['body']}\n")
    except Exception as e:
        logger.error(f"Error viewing pull request: {str(e)}")
        click.echo(f"Error: {str(e)}")


# Release management commands group
@main.group()
def release():
    """Release management commands."""
    pass


@release.command()
@click.option("--directory", default=".", help="Base directory (default: current directory)")
@click.option("--version", help="New version string (default: increment patch version)")
@click.option("--pattern", help="Regex pattern to match version (default: semantic versioning)")
@click.option("--file", "files", multiple=True, help="File to update (can be specified multiple times)")
def update_version_cmd(directory, version, pattern, files):
    """Update version identifiers in files."""
    logger.debug(f"Updating version identifiers in {directory}")
    try:
        # Convert files to list if provided
        files_list = list(files) if files else None

        # Update version
        result = update_version(directory, version, pattern, files_list)

        logger.info(f"Updated version from {result['old_version']} to {result['new_version']}")
        click.echo(f"Updated version from {result['old_version']} to {result['new_version']}")

        if result['updated_files']:
            click.echo("\nUpdated files:")
            for file_path in result['updated_files']:
                click.echo(f"  {file_path}")
        else:
            click.echo("No files were updated.")
    except Exception as e:
        logger.error(f"Error updating version: {str(e)}")
        click.echo(f"Error: {str(e)}")


@release.command()
@click.argument("tag_name")
@click.option("--message", help="Tag message (default: 'Release TAG_NAME')")
@click.option("--directory", default=".", help="Repository directory (default: current directory)")
@click.option("--sign", is_flag=True, help="Create a signed tag")
@click.option("--push", is_flag=True, help="Push tag to remote after creation")
@click.option("--remote", default="origin", help="Remote name for pushing (default: origin)")
def tag(tag_name, message, directory, sign, push, remote):
    """Create a Git tag for the current commit."""
    logger.debug(f"Creating tag {tag_name}")
    try:
        # Create tag
        created_tag = create_tag(tag_name, message, directory, sign)

        logger.info(f"Created tag {created_tag}")
        click.echo(f"Created tag {created_tag}")

        # Push tag if requested
        if push:
            push_tag(created_tag, remote, directory)
            click.echo(f"Pushed tag {created_tag} to {remote}")
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        click.echo(f"Error: {str(e)}")


@release.command()
@click.argument("tag_name")
@click.option("--previous-tag", help="Previous tag name for comparison")
@click.option("--directory", default=".", help="Repository directory (default: current directory)")
@click.option("--output", help="Output file for release notes (default: print to console)")
def notes(tag_name, previous_tag, directory, output):
    """Generate release notes from Git commits."""
    logger.debug(f"Generating release notes for {tag_name}")
    try:
        # Generate release notes
        notes = generate_release_notes(tag_name, previous_tag, directory)

        # Output release notes
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(notes)
            logger.info(f"Wrote release notes to {output}")
            click.echo(f"Wrote release notes to {output}")
        else:
            click.echo(notes)
    except Exception as e:
        logger.error(f"Error generating release notes: {str(e)}")
        click.echo(f"Error: {str(e)}")


@release.command()
@click.argument("repo_name")
@click.argument("tag_name")
@click.option("--name", help="Release title (default: tag name)")
@click.option("--notes-file", help="File containing release notes")
@click.option("--draft", is_flag=True, help="Create as draft release")
@click.option("--prerelease", is_flag=True, help="Mark as prerelease")
@click.option("--asset", multiple=True, help="Asset file to upload (can be specified multiple times)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def publish(repo_name, tag_name, name, notes_file, draft, prerelease, asset, token):
    """Create a GitHub release and optionally upload assets."""
    logger.debug(f"Creating GitHub release for {repo_name} with tag {tag_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Read release notes from file if provided
        body = None
        if notes_file:
            with open(notes_file, "r", encoding="utf-8") as f:
                body = f.read()

        # Create release
        release = create_github_release(repo_name, tag_name, name, body, draft, prerelease, token)

        logger.info(f"Created GitHub release {tag_name} for {repo_name}")
        click.echo(f"Created GitHub release: {release['name']}")
        click.echo(f"URL: {release['html_url']}")

        # Upload assets if provided
        if asset:
            click.echo("\nUploading assets:")
            for asset_path in asset:
                try:
                    asset_info = upload_release_asset(repo_name, release['id'], asset_path, None, token)
                    click.echo(f"  Uploaded {asset_info['name']} ({asset_info['size']} bytes)")
                    click.echo(f"  URL: {asset_info['browser_download_url']}")
                except Exception as e:
                    logger.error(f"Error uploading asset {asset_path}: {str(e)}")
                    click.echo(f"  Error uploading {asset_path}: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating GitHub release: {str(e)}")
        click.echo(f"Error: {str(e)}")


# Workflow automation and monitoring commands group
@main.group()
def workflow():
    """Workflow automation and monitoring commands."""
    pass


@workflow.command("list")
@click.argument("repo_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_workflows_cmd(repo_name, token):
    """List GitHub Actions workflows for a repository."""
    logger.debug(f"Listing workflows for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List workflows
        workflows = list_workflows(repo_name, token)

        if not workflows:
            logger.info(f"No workflows found for {repo_name}")
            click.echo(f"No workflows found for {repo_name}")
            return

        # Display workflows
        headers = ["ID", "Name", "Path", "State", "Updated"]
        table_data = [
            [
                workflow["id"],
                workflow["name"],
                workflow["path"],
                workflow["state"],
                workflow["updated_at"],
            ] for workflow in workflows
        ]

        click.echo(f"Workflows for {repo_name}:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command()
@click.argument("repo_name")
@click.argument("workflow_id")
@click.option("--ref", default="main", help="Git reference (branch, tag, SHA) (default: main)")
@click.option("--input", "inputs", multiple=True, help="Workflow input in format 'key=value' (can be specified multiple times)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--monitor", is_flag=True, help="Monitor workflow run until completion")
@click.option("--interval", default=5, help="Polling interval in seconds for monitoring (default: 5)")
@click.option("--timeout", default=300, help="Timeout in seconds for monitoring (default: 300)")
def trigger(repo_name, workflow_id, ref, inputs, token, monitor, interval, timeout):
    """Trigger a GitHub Actions workflow run."""
    logger.debug(f"Triggering workflow {workflow_id} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Parse inputs
        input_dict = {}
        for input_str in inputs:
            key, value = input_str.split("=", 1)
            input_dict[key] = value

        # Trigger workflow
        run = trigger_workflow(repo_name, workflow_id, ref, input_dict, token)

        logger.info(f"Triggered workflow {workflow_id} in {repo_name}")
        click.echo(f"Triggered workflow: {run['workflow_name']}")
        click.echo(f"URL: {run['url']}")

        # Monitor workflow run if requested
        if monitor and run.get("run_id"):
            click.echo("\nMonitoring workflow run...")
            run_info = monitor_workflow_run(repo_name, run["run_id"], interval, timeout, token)

            if run_info.get("timed_out"):
                click.echo(f"Monitoring timed out after {timeout} seconds")
                click.echo(f"Current status: {run_info['status']}")
            else:
                click.echo(f"Workflow run completed with conclusion: {run_info['conclusion']}")
    except Exception as e:
        logger.error(f"Error triggering workflow: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("runs")
@click.argument("repo_name")
@click.option("--workflow", help="Filter by workflow ID or file name")
@click.option("--status", type=click.Choice(["queued", "in_progress", "completed"]), help="Filter by status")
@click.option("--branch", help="Filter by branch name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_runs(repo_name, workflow, status, branch, token):
    """List GitHub Actions workflow runs for a repository."""
    logger.debug(f"Listing workflow runs for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List workflow runs
        runs = list_workflow_runs(repo_name, workflow, status, branch, token)

        if not runs:
            logger.info(f"No workflow runs found for {repo_name}")
            click.echo(f"No workflow runs found for {repo_name}")
            return

        # Display workflow runs
        headers = ["ID", "Name", "Status", "Conclusion", "Branch", "Created"]
        table_data = [
            [
                run["id"],
                run["name"],
                run["status"],
                run["conclusion"] or "N/A",
                run["branch"],
                run["created_at"],
            ] for run in runs
        ]

        click.echo(f"Workflow runs for {repo_name}:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    except Exception as e:
        logger.error(f"Error listing workflow runs: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("view")
@click.argument("repo_name")
@click.argument("run_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def view_run(repo_name, run_id, token):
    """View detailed information about a workflow run."""
    logger.debug(f"Viewing workflow run {run_id} from repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Get workflow run
        run = get_workflow_run(repo_name, run_id, token)

        # Display workflow run information
        click.echo(f"Workflow Run: {run['name']} (#{run['id']})")
        click.echo(f"Status: {run['status']}")
        click.echo(f"Conclusion: {run['conclusion'] or 'N/A'}")
        click.echo(f"Branch: {run['branch']}")
        click.echo(f"Commit: {run['commit']}")
        click.echo(f"Created: {run['created_at']}")
        click.echo(f"Updated: {run['updated_at']}")
        click.echo(f"URL: {run['url']}")

        # Display jobs
        if run["jobs"]:
            click.echo("\nJobs:")
            for job in run["jobs"]:
                click.echo(f"\n  {job['name']} - {job['status']} ({job['conclusion'] or 'N/A'})")
                click.echo(f"  Started: {job['started_at'] or 'N/A'}")
                click.echo(f"  Completed: {job['completed_at'] or 'N/A'}")

                # Display steps
                if job["steps"]:
                    click.echo("\n  Steps:")
                    for step in job["steps"]:
                        click.echo(f"    {step['number']}. {step['name']} - {step['status']} ({step['conclusion'] or 'N/A'})")
        else:
            click.echo("\nNo jobs found for this workflow run.")
    except Exception as e:
        logger.error(f"Error viewing workflow run: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command()
@click.argument("repo_name")
@click.argument("run_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def cancel(repo_name, run_id, token):
    """Cancel a workflow run."""
    logger.debug(f"Cancelling workflow run {run_id} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Cancel workflow run
        result = cancel_workflow_run(repo_name, run_id, token)

        if result:
            logger.info(f"Cancelled workflow run {run_id} in {repo_name}")
            click.echo(f"Cancelled workflow run {run_id}")
        else:
            logger.warning(f"Failed to cancel workflow run {run_id} in {repo_name}")
            click.echo(f"Failed to cancel workflow run {run_id}")
    except Exception as e:
        logger.error(f"Error cancelling workflow run: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command()
@click.argument("repo_name")
@click.argument("run_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def rerun(repo_name, run_id, token):
    """Rerun a workflow run."""
    logger.debug(f"Rerunning workflow run {run_id} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Rerun workflow run
        result = rerun_workflow_run(repo_name, run_id, token)

        if result:
            logger.info(f"Reran workflow run {run_id} in {repo_name}")
            click.echo(f"Reran workflow run {run_id}")
        else:
            logger.warning(f"Failed to rerun workflow run {run_id} in {repo_name}")
            click.echo(f"Failed to rerun workflow run {run_id}")
    except Exception as e:
        logger.error(f"Error rerunning workflow run: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("secrets")
@click.argument("repo_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_secrets(repo_name, token):
    """List repository secrets."""
    logger.debug(f"Listing secrets for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List secrets
        secrets = list_repository_secrets(repo_name, token)

        if not secrets:
            logger.info(f"No secrets found for {repo_name}")
            click.echo(f"No secrets found for {repo_name}")
            return

        # Display secrets
        headers = ["Name", "Created", "Updated"]
        table_data = [
            [
                secret["name"],
                secret["created_at"],
                secret["updated_at"],
            ] for secret in secrets
        ]

        click.echo(f"Secrets for {repo_name}:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    except Exception as e:
        logger.error(f"Error listing secrets: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("set-secret")
@click.argument("repo_name")
@click.argument("secret_name")
@click.option("--value", prompt=True, hide_input=True, help="Secret value")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def set_secret(repo_name, secret_name, value, token):
    """Create or update a repository secret."""
    logger.debug(f"Setting secret {secret_name} for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Create or update secret
        result = create_repository_secret(repo_name, secret_name, value, token)

        if result:
            logger.info(f"Set secret {secret_name} for {repo_name}")
            click.echo(f"Successfully set secret {secret_name}")
        else:
            logger.warning(f"Failed to set secret {secret_name} for {repo_name}")
            click.echo(f"Failed to set secret {secret_name}")
    except Exception as e:
        logger.error(f"Error setting secret: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("delete-secret")
@click.argument("repo_name")
@click.argument("secret_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def delete_secret(repo_name, secret_name, token):
    """Delete a repository secret."""
    logger.debug(f"Deleting secret {secret_name} from repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Delete secret
        result = delete_repository_secret(repo_name, secret_name, token)

        if result:
            logger.info(f"Deleted secret {secret_name} from {repo_name}")
            click.echo(f"Successfully deleted secret {secret_name}")
        else:
            logger.warning(f"Failed to delete secret {secret_name} from {repo_name}")
            click.echo(f"Failed to delete secret {secret_name}")
    except Exception as e:
        logger.error(f"Error deleting secret: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("caches")
@click.argument("repo_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_caches(repo_name, token):
    """List GitHub Actions caches for a repository."""
    logger.debug(f"Listing workflow caches for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List caches
        caches = list_workflow_caches(repo_name, token)

        if not caches:
            logger.info(f"No workflow caches found for {repo_name}")
            click.echo(f"No workflow caches found for {repo_name}")
            return

        # Display caches
        headers = ["ID", "Key", "Ref", "Size (bytes)", "Created"]
        table_data = [
            [
                cache["id"],
                cache["key"],
                cache["ref"],
                cache["size"],
                cache["created_at"],
            ] for cache in caches
        ]

        click.echo(f"Workflow caches for {repo_name}:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    except Exception as e:
        logger.error(f"Error listing workflow caches: {str(e)}")
        click.echo(f"Error: {str(e)}")


@workflow.command("delete-cache")
@click.argument("repo_name")
@click.option("--id", "cache_id", help="Cache ID to delete")
@click.option("--key", "cache_key", help="Cache key to delete")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def delete_cache(repo_name, cache_id, cache_key, token):
    """Delete a GitHub Actions cache."""
    logger.debug(f"Deleting workflow cache from repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not cache_id and not cache_key:
        logger.error("Either --id or --key must be provided")
        click.echo("Error: Either --id or --key must be provided")
        return

    try:
        # Delete cache
        result = delete_workflow_cache(repo_name, cache_id, cache_key, token)

        if result:
            if cache_id:
                logger.info(f"Deleted workflow cache {cache_id} from {repo_name}")
                click.echo(f"Successfully deleted workflow cache {cache_id}")
            else:
                logger.info(f"Deleted workflow cache with key {cache_key} from {repo_name}")
                click.echo(f"Successfully deleted workflow cache with key {cache_key}")
        else:
            logger.warning(f"Failed to delete workflow cache from {repo_name}")
            click.echo(f"Failed to delete workflow cache")
    except Exception as e:
        logger.error(f"Error deleting workflow cache: {str(e)}")
        click.echo(f"Error: {str(e)}")


# Gist management commands group
@main.group()
def gist():
    """Gist management commands."""
    pass


@gist.command("list")
@click.option("--public", is_flag=True, help="List only public gists")
@click.option("--starred", is_flag=True, help="List starred gists instead of owned gists")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--format", type=click.Choice(["table", "simple"]), default="simple",
              help="Output format (default: simple)")
def list_gists_cmd(public, starred, token, format):
    """List GitHub Gists for the authenticated user."""
    logger.debug(f"Listing {'public' if public else 'all'} {'starred' if starred else 'owned'} gists")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List gists
        gists = list_gists(public, starred, token)

        if not gists:
            logger.info(f"No gists found")
            click.echo(f"No gists found")
            return

        # Display gists
        if format == "table":
            headers = ["ID", "Description", "Files", "Public", "Updated"]
            table_data = [
                [
                    gist["id"],
                    (gist["description"] or "")[:30] + ("..." if len(gist["description"] or "") > 30 else ""),
                    ", ".join(list(gist["files"].keys())),
                    "Yes" if gist["public"] else "No",
                    gist["updated_at"],
                ] for gist in gists
            ]

            click.echo(f"{'Public' if public else 'All'} {'starred' if starred else 'owned'} gists:")
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Simple format
            click.echo(f"{'Public' if public else 'All'} {'starred' if starred else 'owned'} gists:")
            for gist in gists:
                files_str = ", ".join(list(gist["files"].keys()))
                visibility = "public" if gist["public"] else "private"
                desc = f": {gist['description']}" if gist["description"] else ""
                click.echo(f"{gist['id']} [{visibility}] [{files_str}]{desc}")
    except Exception as e:
        logger.error(f"Error listing gists: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("view")
@click.argument("gist_id")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--raw", is_flag=True, help="Show raw file content")
def view_gist(gist_id, token, raw):
    """View detailed information about a gist."""
    logger.debug(f"Viewing gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Get gist
        gist = get_gist(gist_id, token)

        # Display gist information
        click.echo(f"Gist: {gist['id']}")
        click.echo(f"Description: {gist['description'] or 'N/A'}")
        click.echo(f"Visibility: {'Public' if gist['public'] else 'Private'}")
        click.echo(f"Owner: {gist['owner'] or 'N/A'}")
        click.echo(f"Created: {gist['created_at']}")
        click.echo(f"Updated: {gist['updated_at']}")
        click.echo(f"URL: {gist['url']}")

        # Check if gist is starred
        try:
            starred = is_gist_starred(gist_id, token)
            click.echo(f"Starred: {'Yes' if starred else 'No'}")
        except Exception:
            pass

        # Display files
        click.echo(f"\nFiles ({len(gist['files'])}):")
        for filename, file_info in gist["files"].items():
            click.echo(f"\n  {filename} ({file_info['language'] or 'Unknown'}, {file_info['size']} bytes)")
            if raw:
                click.echo("\n" + file_info["content"])
            else:
                # Show first 5 lines
                lines = file_info["content"].split("\n")[:5]
                click.echo("\n  " + "\n  ".join(lines))
                if len(file_info["content"].split("\n")) > 5:
                    click.echo("  ...")

        # Display comments
        if gist["comments"]:
            click.echo(f"\nComments ({len(gist['comments'])}):")
            for i, comment in enumerate(gist["comments"], 1):
                click.echo(f"\n  Comment #{i} by {comment['user']} on {comment['created_at']}:")
                click.echo(f"  {comment['body']}")
    except Exception as e:
        logger.error(f"Error viewing gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("create")
@click.option("--file", "files", multiple=True, help="File to include (can be specified multiple times)")
@click.option("--content", multiple=True, help="File content in format 'filename:content' (can be specified multiple times)")
@click.option("--description", help="Gist description")
@click.option("--public/--private", default=False, help="Whether the gist is public (default: private)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def create_gist_cmd(files, content, description, public, token):
    """Create a new gist."""
    logger.debug(f"Creating {'public' if public else 'private'} gist")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not files and not content:
        logger.error("No files or content provided")
        click.echo("Error: You must provide at least one file (--file) or content (--content)")
        return

    try:
        # Prepare files dictionary
        files_dict = {}

        # Add files from --file option
        for file_path in files:
            if not os.path.isfile(file_path):
                logger.error(f"File {file_path} does not exist")
                click.echo(f"Error: File {file_path} does not exist")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            filename = os.path.basename(file_path)
            files_dict[filename] = file_content

        # Add content from --content option
        for content_str in content:
            if ":" not in content_str:
                logger.error(f"Invalid content format: {content_str}")
                click.echo(f"Error: Invalid content format: {content_str}. Use 'filename:content'")
                continue

            filename, file_content = content_str.split(":", 1)
            files_dict[filename] = file_content

        if not files_dict:
            logger.error("No valid files or content provided")
            click.echo("Error: No valid files or content provided")
            return

        # Create gist
        gist = create_gist(files_dict, description or "", public, token)

        logger.info(f"Created gist {gist['id']}")
        click.echo(f"Created gist: {gist['id']}")
        click.echo(f"URL: {gist['url']}")
        click.echo(f"Files: {', '.join(list(gist['files'].keys()))}")
    except Exception as e:
        logger.error(f"Error creating gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("update")
@click.argument("gist_id")
@click.option("--file", "files", multiple=True, help="File to update (can be specified multiple times)")
@click.option("--content", multiple=True, help="File content in format 'filename:content' (can be specified multiple times)")
@click.option("--description", help="New gist description")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def update_gist_cmd(gist_id, files, content, description, token):
    """Update an existing gist."""
    logger.debug(f"Updating gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not files and not content and description is None:
        logger.error("No updates provided")
        click.echo("Error: You must provide at least one file (--file), content (--content), or description (--description)")
        return

    try:
        # Prepare files dictionary
        files_dict = {}

        # Add files from --file option
        for file_path in files:
            if not os.path.isfile(file_path):
                logger.error(f"File {file_path} does not exist")
                click.echo(f"Error: File {file_path} does not exist")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            filename = os.path.basename(file_path)
            files_dict[filename] = file_content

        # Add content from --content option
        for content_str in content:
            if ":" not in content_str:
                logger.error(f"Invalid content format: {content_str}")
                click.echo(f"Error: Invalid content format: {content_str}. Use 'filename:content'")
                continue

            filename, file_content = content_str.split(":", 1)
            files_dict[filename] = file_content

        # Update gist
        gist = update_gist(gist_id, files_dict if files_dict else None, description, token)

        logger.info(f"Updated gist {gist_id}")
        click.echo(f"Updated gist: {gist['id']}")
        click.echo(f"URL: {gist['url']}")
        click.echo(f"Files: {', '.join(list(gist['files'].keys()))}")
    except Exception as e:
        logger.error(f"Error updating gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("delete")
@click.argument("gist_id")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_gist_cmd(gist_id, token, confirm):
    """Delete a gist."""
    logger.debug(f"Deleting gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete gist {gist_id}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete gist
        result = delete_gist(gist_id, token)

        if result:
            logger.info(f"Deleted gist {gist_id}")
            click.echo(f"Deleted gist {gist_id}")
        else:
            logger.warning(f"Failed to delete gist {gist_id}")
            click.echo(f"Failed to delete gist {gist_id}")
    except Exception as e:
        logger.error(f"Error deleting gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("star")
@click.argument("gist_id")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def star_gist_cmd(gist_id, token):
    """Star a gist."""
    logger.debug(f"Starring gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Star gist
        result = star_gist(gist_id, token)

        if result:
            logger.info(f"Starred gist {gist_id}")
            click.echo(f"Starred gist {gist_id}")
        else:
            logger.warning(f"Failed to star gist {gist_id}")
            click.echo(f"Failed to star gist {gist_id}")
    except Exception as e:
        logger.error(f"Error starring gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("unstar")
@click.argument("gist_id")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def unstar_gist_cmd(gist_id, token):
    """Unstar a gist."""
    logger.debug(f"Unstarring gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Unstar gist
        result = unstar_gist(gist_id, token)

        if result:
            logger.info(f"Unstarred gist {gist_id}")
            click.echo(f"Unstarred gist {gist_id}")
        else:
            logger.warning(f"Failed to unstar gist {gist_id}")
            click.echo(f"Failed to unstar gist {gist_id}")
    except Exception as e:
        logger.error(f"Error unstarring gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("comment")
@click.argument("gist_id")
@click.argument("body")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def comment_gist(gist_id, body, token):
    """Add a comment to a gist."""
    logger.debug(f"Adding comment to gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Add comment
        comment = add_gist_comment(gist_id, body, token)

        logger.info(f"Added comment to gist {gist_id}")
        click.echo(f"Added comment to gist {gist_id}")
        click.echo(f"Comment ID: {comment['id']}")
    except Exception as e:
        logger.error(f"Error adding comment to gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("delete-comment")
@click.argument("gist_id")
@click.argument("comment_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_comment(gist_id, comment_id, token, confirm):
    """Delete a comment from a gist."""
    logger.debug(f"Deleting comment {comment_id} from gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete comment {comment_id} from gist {gist_id}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete comment
        result = delete_gist_comment(gist_id, comment_id, token)

        if result:
            logger.info(f"Deleted comment {comment_id} from gist {gist_id}")
            click.echo(f"Deleted comment {comment_id} from gist {gist_id}")
        else:
            logger.warning(f"Failed to delete comment {comment_id} from gist {gist_id}")
            click.echo(f"Failed to delete comment {comment_id} from gist {gist_id}")
    except Exception as e:
        logger.error(f"Error deleting comment from gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("fork")
@click.argument("gist_id")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def fork_gist_cmd(gist_id, token):
    """Fork a gist."""
    logger.debug(f"Forking gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Fork gist
        forked_gist = fork_gist(gist_id, token)

        logger.info(f"Forked gist {gist_id} to {forked_gist['id']}")
        click.echo(f"Forked gist {gist_id} to {forked_gist['id']}")
        click.echo(f"URL: {forked_gist['url']}")
    except Exception as e:
        logger.error(f"Error forking gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("download")
@click.argument("gist_id")
@click.option("--directory", help="Directory to save files to (default: current directory)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def download_gist_cmd(gist_id, directory, token):
    """Download a gist to the local filesystem."""
    logger.debug(f"Downloading gist {gist_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Download gist
        downloaded_files = download_gist(gist_id, directory, token)

        logger.info(f"Downloaded {len(downloaded_files)} files from gist {gist_id}")
        click.echo(f"Downloaded {len(downloaded_files)} files from gist {gist_id}:")
        for file_path in downloaded_files:
            click.echo(f"  {file_path}")
    except Exception as e:
        logger.error(f"Error downloading gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


@gist.command("upload")
@click.argument("files_or_directory", nargs=-1, required=True)
@click.option("--description", help="Gist description")
@click.option("--public/--private", default=False, help="Whether the gist is public (default: private)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def upload_gist_cmd(files_or_directory, description, public, token):
    """Upload files to a new gist."""
    logger.debug(f"Uploading files to a new gist")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Upload files
        gist_info = upload_gist(list(files_or_directory), description or "", public, token)

        logger.info(f"Uploaded files to gist {gist_info['id']}")
        click.echo(f"Uploaded files to gist {gist_info['id']}")
        click.echo(f"URL: {gist_info['url']}")
        click.echo(f"Files: {', '.join(list(gist_info['files'].keys()))}")
    except Exception as e:
        logger.error(f"Error uploading files to gist: {str(e)}")
        click.echo(f"Error: {str(e)}")


# Project templates and scaffolding commands group
@main.group()
def template():
    """Project templates and scaffolding commands."""
    pass


@template.command("list")
@click.option("--templates-dir", help="Directory containing templates")
@click.option("--format", type=click.Choice(["table", "simple"]), default="simple",
              help="Output format (default: simple)")
def list_templates_cmd(templates_dir, format):
    """List available project templates."""
    logger.debug(f"Listing templates from {templates_dir or 'default directory'}")
    try:
        # List templates
        templates = list_templates(templates_dir)

        if not templates:
            logger.info(f"No templates found")
            click.echo(f"No templates found")
            return

        # Display templates
        if format == "table":
            headers = ["Name", "Description", "Version", "Directory"]
            table_data = [
                [
                    template["name"],
                    template["description"],
                    template.get("version", "unknown"),
                    template["directory"],
                ] for template in templates
            ]

            click.echo(f"Available templates:")
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Simple format
            click.echo(f"Available templates:")
            for template in templates:
                click.echo(f"{template['name']} - {template['description']}")
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("view")
@click.argument("template_name")
@click.option("--templates-dir", help="Directory containing templates")
@click.option("--show-variables", is_flag=True, help="Show template variables")
def view_template(template_name, templates_dir, show_variables):
    """View detailed information about a template."""
    logger.debug(f"Viewing template {template_name}")
    try:
        # Get template
        template = get_template(template_name, templates_dir)

        if not template:
            logger.error(f"Template {template_name} not found")
            click.echo(f"Error: Template {template_name} not found")
            return

        # Display template information
        click.echo(f"Template: {template['name']}")
        click.echo(f"Description: {template['description']}")
        click.echo(f"Version: {template.get('version', 'unknown')}")
        click.echo(f"Directory: {template['directory']}")

        # Show variables if requested
        if show_variables:
            variables = list_template_variables(template_name, templates_dir)

            if variables:
                click.echo("\nVariables:")
                for name, info in variables.items():
                    if isinstance(info, dict):
                        description = info.get("description", "")
                        default = info.get("default", "None")
                        click.echo(f"  {name}: {description} (default: {default})")
                    else:
                        click.echo(f"  {name}: {info}")
            else:
                click.echo("\nNo variables defined for this template.")
    except Exception as e:
        logger.error(f"Error viewing template: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("create")
@click.argument("name")
@click.argument("source_dir")
@click.option("--description", help="Template description")
@click.option("--version", default="1.0.0", help="Template version (default: 1.0.0)")
@click.option("--templates-dir", help="Directory to save template to")
def create_template_cmd(name, source_dir, description, version, templates_dir):
    """Create a new template from a directory."""
    logger.debug(f"Creating template {name} from {source_dir}")
    try:
        # Validate source directory
        if not os.path.isdir(source_dir):
            logger.error(f"Source directory {source_dir} does not exist")
            click.echo(f"Error: Source directory {source_dir} does not exist")
            return

        # Create template
        template = create_template(
            source_dir,
            name,
            description or f"Template created from {source_dir}",
            version,
            None,
            templates_dir
        )

        logger.info(f"Created template {name}")
        click.echo(f"Created template: {template['name']}")
        click.echo(f"Description: {template['description']}")
        click.echo(f"Version: {template['version']}")
        click.echo(f"Directory: {template['directory']}")
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("delete")
@click.argument("template_name")
@click.option("--templates-dir", help="Directory containing templates")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_template_cmd(template_name, templates_dir, confirm):
    """Delete a template."""
    logger.debug(f"Deleting template {template_name}")
    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete template {template_name}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete template
        result = delete_template(template_name, templates_dir)

        if result:
            logger.info(f"Deleted template {template_name}")
            click.echo(f"Deleted template {template_name}")
        else:
            logger.warning(f"Failed to delete template {template_name}")
            click.echo(f"Failed to delete template {template_name}")
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("import-github")
@click.argument("repo_name")
@click.option("--path", help="Path within repository to use as template")
@click.option("--name", help="Template name (default: repository name)")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--templates-dir", help="Directory to save template to")
def import_template_from_github_cmd(repo_name, path, name, token, templates_dir):
    """Import a template from a GitHub repository."""
    logger.debug(f"Importing template from GitHub repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Import template
        template = import_template_from_github(
            repo_name,
            path,
            name,
            token,
            templates_dir
        )

        logger.info(f"Imported template {template['name']} from {repo_name}")
        click.echo(f"Imported template: {template['name']}")
        click.echo(f"Description: {template['description']}")
        click.echo(f"Version: {template['version']}")
        click.echo(f"Directory: {template['directory']}")
    except Exception as e:
        logger.error(f"Error importing template from GitHub: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("import-url")
@click.argument("url")
@click.argument("name")
@click.option("--description", help="Template description")
@click.option("--templates-dir", help="Directory to save template to")
def import_template_from_url_cmd(url, name, description, templates_dir):
    """Import a template from a URL."""
    logger.debug(f"Importing template from URL {url}")
    try:
        # Import template
        template = import_template_from_url(
            url,
            name,
            description,
            templates_dir
        )

        logger.info(f"Imported template {template['name']} from {url}")
        click.echo(f"Imported template: {template['name']}")
        click.echo(f"Description: {template['description']}")
        click.echo(f"Version: {template['version']}")
        click.echo(f"Directory: {template['directory']}")
    except Exception as e:
        logger.error(f"Error importing template from URL: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("generate")
@click.argument("template_name")
@click.argument("output_dir")
@click.option("--var", "variables", multiple=True, help="Template variable in format 'name=value' (can be specified multiple times)")
@click.option("--templates-dir", help="Directory containing templates")
def generate_project_cmd(template_name, output_dir, variables, templates_dir):
    """Generate a project from a template."""
    logger.debug(f"Generating project from template {template_name} in {output_dir}")
    try:
        # Parse variables
        vars_dict = {}
        for var in variables:
            if "=" in var:
                name, value = var.split("=", 1)
                vars_dict[name] = value
            else:
                logger.warning(f"Invalid variable format: {var}")
                click.echo(f"Warning: Invalid variable format: {var}. Use 'name=value'.")

        # Generate project
        output = generate_project(template_name, output_dir, vars_dict, templates_dir)

        logger.info(f"Generated project from template {template_name} in {output}")
        click.echo(f"Generated project from template {template_name} in {output}")
    except Exception as e:
        logger.error(f"Error generating project from template: {str(e)}")
        click.echo(f"Error: {str(e)}")


@template.command("variables")
@click.argument("template_name")
@click.option("--templates-dir", help="Directory containing templates")
def list_template_variables_cmd(template_name, templates_dir):
    """List variables for a template."""
    logger.debug(f"Listing variables for template {template_name}")
    try:
        # Get template variables
        variables = list_template_variables(template_name, templates_dir)

        if not variables:
            logger.info(f"No variables defined for template {template_name}")
            click.echo(f"No variables defined for template {template_name}")
            return

        # Display variables
        click.echo(f"Variables for template {template_name}:")
        for name, info in variables.items():
            if isinstance(info, dict):
                description = info.get("description", "")
                default = info.get("default", "None")
                required = "Required" if info.get("required", False) else "Optional"
                click.echo(f"  {name}: {description} (default: {default}, {required})")
            else:
                click.echo(f"  {name}: {info}")
    except Exception as e:
        logger.error(f"Error listing template variables: {str(e)}")
        click.echo(f"Error: {str(e)}")


# Project management commands group
@main.group()
def project():
    """Project management commands."""
    pass


@project.command("list")
@click.argument("repo_name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--format", type=click.Choice(["table", "simple"]), default="simple",
              help="Output format (default: simple)")
def list_projects(repo_name, token, format):
    """List project boards for a repository."""
    logger.debug(f"Listing project boards for repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # List project boards
        projects = list_project_boards(repo_name, token)

        if not projects:
            logger.info(f"No project boards found for {repo_name}")
            click.echo(f"No project boards found for {repo_name}")
            return

        # Display project boards
        if format == "table":
            headers = ["ID", "Name", "State", "Columns", "Updated"]
            table_data = [
                [
                    project["id"],
                    project["name"],
                    project["state"],
                    len(project["columns"]),
                    project["updated_at"],
                ] for project in projects
            ]

            click.echo(f"Project boards for {repo_name}:")
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Simple format
            click.echo(f"Project boards for {repo_name}:")
            for project in projects:
                columns_str = ", ".join([column["name"] for column in project["columns"]])
                click.echo(f"{project['id']}: {project['name']} [{project['state']}] - Columns: {columns_str}")
    except Exception as e:
        logger.error(f"Error listing project boards: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("view")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def view_project(repo_name, project_id, token):
    """View detailed information about a project board."""
    logger.debug(f"Viewing project board {project_id} from repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Get project board
        project = get_project_board(repo_name, project_id, token)

        # Display project information
        click.echo(f"Project: {project['name']} (#{project['id']})")
        click.echo(f"State: {project['state']}")
        click.echo(f"Created: {project['created_at']}")
        click.echo(f"Updated: {project['updated_at']}")
        click.echo(f"URL: {project['html_url']}")

        if project["body"]:
            click.echo(f"\nDescription:\n{project['body']}")

        # Display columns
        click.echo(f"\nColumns ({len(project['columns'])}):")
        for column in project["columns"]:
            click.echo(f"\n  {column['name']} (#{column['id']}) - {len(column['cards'])} cards")

            # Display cards
            if column["cards"]:
                for card in column["cards"]:
                    if "content" in card and card["content"]:
                        content = card["content"]
                        click.echo(f"    #{content['number']} {content['title']} [{content['state']}] ({content['type']})")
                    elif card["note"]:
                        note = card["note"].replace("\n", " ")[:50]
                        if len(card["note"]) > 50:
                            note += "..."
                        click.echo(f"    Note: {note}")
                    else:
                        click.echo(f"    Card #{card['id']}")
    except Exception as e:
        logger.error(f"Error viewing project board: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("create")
@click.argument("repo_name")
@click.argument("name")
@click.option("--body", help="Project description")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def create_project(repo_name, name, body, token):
    """Create a new project board."""
    logger.debug(f"Creating project board {name} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Create project board
        project = create_project_board(repo_name, name, body, token)

        logger.info(f"Created project board {name} in {repo_name}")
        click.echo(f"Created project board: {project['name']} (#{project['id']})")
        click.echo(f"URL: {project['html_url']}")
    except Exception as e:
        logger.error(f"Error creating project board: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("create-from-template")
@click.argument("repo_name")
@click.argument("name")
@click.argument("template", type=click.Choice(["basic", "automated", "bug_triage"]))
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def create_project_from_template_cmd(repo_name, name, template, token):
    """Create a project board from a template."""
    logger.debug(f"Creating project board {name} from template {template} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Create project from template
        project = create_project_from_template(repo_name, name, template, token)

        logger.info(f"Created project board {name} from template {template} in {repo_name}")
        click.echo(f"Created project board: {project['name']} (#{project['id']})")
        click.echo(f"URL: {project['html_url']}")

        # Display columns
        click.echo(f"\nColumns:")
        for column in project["columns"]:
            click.echo(f"  {column['name']} (#{column['id']})")
    except Exception as e:
        logger.error(f"Error creating project from template: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("add-column")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("name")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def add_column(repo_name, project_id, name, token):
    """Add a column to a project board."""
    logger.debug(f"Adding column {name} to project {project_id} in repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Create column
        column = create_project_column(repo_name, project_id, name, token)

        logger.info(f"Added column {name} to project {project_id} in {repo_name}")
        click.echo(f"Added column: {column['name']} (#{column['id']})")
    except Exception as e:
        logger.error(f"Error adding column to project: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("add-issue")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("column_id", type=int)
@click.argument("issue_number", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def add_issue(repo_name, project_id, column_id, issue_number, token):
    """Add an issue to a project board column."""
    logger.debug(f"Adding issue {issue_number} to column {column_id} in project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Add issue to project
        card = add_issue_to_project(repo_name, project_id, column_id, issue_number, token)

        logger.info(f"Added issue {issue_number} to column {column_id} in project {project_id}")
        click.echo(f"Added issue #{issue_number} to project as card #{card['id']}")
    except Exception as e:
        logger.error(f"Error adding issue to project: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("add-pr")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("column_id", type=int)
@click.argument("pr_number", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def add_pr(repo_name, project_id, column_id, pr_number, token):
    """Add a pull request to a project board column."""
    logger.debug(f"Adding PR {pr_number} to column {column_id} in project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Add PR to project
        card = add_pr_to_project(repo_name, project_id, column_id, pr_number, token)

        logger.info(f"Added PR {pr_number} to column {column_id} in project {project_id}")
        click.echo(f"Added PR #{pr_number} to project as card #{card['id']}")
    except Exception as e:
        logger.error(f"Error adding PR to project: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("add-note")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("column_id", type=int)
@click.argument("note")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def add_note(repo_name, project_id, column_id, note, token):
    """Add a note to a project board column."""
    logger.debug(f"Adding note to column {column_id} in project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Add note to project
        card = add_note_to_project(repo_name, project_id, column_id, note, token)

        logger.info(f"Added note to column {column_id} in project {project_id}")
        click.echo(f"Added note to project as card #{card['id']}")
    except Exception as e:
        logger.error(f"Error adding note to project: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("move-card")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("card_id", type=int)
@click.argument("column_id", type=int)
@click.option("--position", type=click.Choice(["top", "bottom"]), default="top",
              help="Position in column (default: top)")
@click.option("--after", type=int, help="Position card after this card ID")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def move_card(repo_name, project_id, card_id, column_id, position, after, token):
    """Move a card to a different column or position."""
    logger.debug(f"Moving card {card_id} to column {column_id} in project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Determine position
        if after:
            position = f"after:{after}"

        # Move card
        result = move_project_card(repo_name, project_id, card_id, column_id, position, token)

        if result:
            logger.info(f"Moved card {card_id} to column {column_id} in project {project_id}")
            click.echo(f"Moved card #{card_id} to column #{column_id}")
        else:
            logger.warning(f"Failed to move card {card_id} to column {column_id} in project {project_id}")
            click.echo(f"Failed to move card #{card_id} to column #{column_id}")
    except Exception as e:
        logger.error(f"Error moving card: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("delete-card")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("card_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_card(repo_name, project_id, card_id, token, confirm):
    """Delete a card from a project board."""
    logger.debug(f"Deleting card {card_id} from project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete card {card_id} from project {project_id}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete card
        result = delete_project_card(repo_name, project_id, card_id, token)

        if result:
            logger.info(f"Deleted card {card_id} from project {project_id}")
            click.echo(f"Deleted card #{card_id} from project #{project_id}")
        else:
            logger.warning(f"Failed to delete card {card_id} from project {project_id}")
            click.echo(f"Failed to delete card #{card_id} from project #{project_id}")
    except Exception as e:
        logger.error(f"Error deleting card: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("delete-column")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.argument("column_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_column(repo_name, project_id, column_id, token, confirm):
    """Delete a column from a project board."""
    logger.debug(f"Deleting column {column_id} from project {project_id}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete column {column_id} from project {project_id}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete column
        result = delete_project_column(repo_name, project_id, column_id, token)

        if result:
            logger.info(f"Deleted column {column_id} from project {project_id}")
            click.echo(f"Deleted column #{column_id} from project #{project_id}")
        else:
            logger.warning(f"Failed to delete column {column_id} from project {project_id}")
            click.echo(f"Failed to delete column #{column_id} from project #{project_id}")
    except Exception as e:
        logger.error(f"Error deleting column: {str(e)}")
        click.echo(f"Error: {str(e)}")


@project.command("delete")
@click.argument("repo_name")
@click.argument("project_id", type=int)
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_project(repo_name, project_id, token, confirm):
    """Delete a project board."""
    logger.debug(f"Deleting project {project_id} from repository {repo_name}")
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    try:
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete project {project_id} from repository {repo_name}?"):
                click.echo("Deletion cancelled.")
                return

        # Delete project
        result = delete_project_board(repo_name, project_id, token)

        if result:
            logger.info(f"Deleted project {project_id} from repository {repo_name}")
            click.echo(f"Deleted project #{project_id} from repository {repo_name}")
        else:
            logger.warning(f"Failed to delete project {project_id} from repository {repo_name}")
            click.echo(f"Failed to delete project #{project_id} from repository {repo_name}")
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        click.echo(f"Error: {str(e)}")


# System and environment management commands group
@main.group()
def system():
    """System and environment management commands."""
    pass


@system.command("info")
@click.option("--output", help="Output file path")
@click.option("--format", type=click.Choice(["json", "table"]), default="table",
              help="Output format (default: table)")
def system_info(output, format):
    """Get system information."""
    logger.debug("Getting system information")
    try:
        # Get system information
        info = get_system_info()

        if format == "json":
            # Output as JSON
            if output:
                # Write to file
                with open(output, "w") as f:
                    json.dump(info, f, indent=2)
                logger.info(f"System information written to {output}")
                click.echo(f"System information written to {output}")
            else:
                # Print to console
                click.echo(json.dumps(info, indent=2))
        else:
            # Output as table
            click.echo("System Information:")
            click.echo(f"OS: {info['os']} {info['os_release']} {info['os_version']}")
            click.echo(f"Architecture: {info['architecture']}")
            click.echo(f"Processor: {info['processor']}")
            click.echo(f"Python: {info['python_version']} ({info['python_implementation']})")
            click.echo(f"Python Path: {info['python_path']}")

            # Git information
            click.echo(f"\nGit: {info['git_version']}")

            # Installed packages
            click.echo("\nInstalled Packages:")
            packages_table = [[pkg["name"], pkg["version"]] for pkg in info["installed_packages"]]
            click.echo(tabulate(packages_table, headers=["Package", "Version"], tablefmt="simple"))

            # Environment variables (if requested)
            if output:
                # Write full information to file
                with open(output, "w") as f:
                    json.dump(info, f, indent=2)
                logger.info(f"System information written to {output}")
                click.echo(f"\nFull system information written to {output}")
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("check-dependencies")
@click.option("--install-missing", is_flag=True, help="Install missing dependencies")
@click.option("--upgrade", is_flag=True, help="Upgrade dependencies when installing")
def check_dependencies_cmd(install_missing, upgrade):
    """Check dependencies required by HubQueue."""
    logger.debug("Checking dependencies")
    try:
        # Check dependencies
        dependencies = check_dependencies()

        # Display dependencies
        click.echo("Dependencies:")
        for dep, installed in dependencies.items():
            status = "✓" if installed else "✗"
            click.echo(f"{status} {dep}")

        # Install missing dependencies if requested
        if install_missing:
            missing = [dep for dep, installed in dependencies.items() if not installed]
            if missing:
                click.echo(f"\nInstalling missing dependencies: {', '.join(missing)}")
                for dep in missing:
                    click.echo(f"Installing {dep}...")
                    if install_dependency(dep, upgrade):
                        click.echo(f"✓ {dep} installed successfully")
                    else:
                        click.echo(f"✗ Failed to install {dep}")
            else:
                click.echo("\nNo missing dependencies to install")
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("git-config")
@click.option("--set", is_flag=True, help="Set Git configuration")
@click.option("--key", help="Configuration key (required with --set)")
@click.option("--value", help="Configuration value (required with --set)")
@click.option("--global/--local", default=True, help="Set global or local configuration (default: global)")
def git_config(set, key, value, global_config):
    """Check or set Git configuration."""
    logger.debug("Checking Git configuration")
    try:
        if set:
            # Set Git configuration
            if not key or not value:
                logger.error("Key and value are required when setting Git configuration")
                click.echo("Error: Key and value are required when setting Git configuration")
                return

            if set_git_config(key, value, global_config):
                logger.info(f"Git configuration set successfully: {key}={value}")
                click.echo(f"Git configuration set successfully: {key}={value}")
            else:
                logger.error(f"Failed to set Git configuration: {key}={value}")
                click.echo(f"Failed to set Git configuration: {key}={value}")
        else:
            # Check Git configuration
            config = check_git_config()

            if "error" in config:
                logger.error(f"Error checking Git configuration: {config['error']}")
                click.echo(f"Error: {config['error']}")
                return

            click.echo("Git Configuration:")
            for key, value in config.items():
                click.echo(f"{key}: {value or 'Not set'}")
    except Exception as e:
        logger.error(f"Error with Git configuration: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("setup")
@click.option("--force", is_flag=True, help="Force setup even if already configured")
def setup_cmd(force):
    # Note: force parameter is reserved for future use
    """Setup environment for HubQueue."""
    logger.debug("Setting up environment")
    try:
        # Setup environment
        if setup_environment():
            logger.info("Environment setup completed successfully")
            click.echo("Environment setup completed successfully")
        else:
            logger.error("Environment setup failed")
            click.echo("Environment setup failed")
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("export")
@click.option("--output", help="Output file path")
def export_cmd(output):
    """Export environment information to a file."""
    logger.debug("Exporting environment information")
    try:
        # Export environment information
        file_path = export_environment(output)

        logger.info(f"Environment information exported to {file_path}")
        click.echo(f"Environment information exported to {file_path}")
    except Exception as e:
        logger.error(f"Error exporting environment information: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("check-updates")
@click.option("--install", is_flag=True, help="Install updates if available")
def check_updates(install):
    """Check for updates to HubQueue."""
    logger.debug("Checking for updates")
    try:
        # Check for updates
        update_info = check_for_updates()

        if "error" in update_info:
            logger.error(f"Error checking for updates: {update_info['error']}")
            click.echo(f"Error checking for updates: {update_info['error']}")
            return

        click.echo(f"Current version: {update_info['current_version']}")
        click.echo(f"Latest version: {update_info['latest_version']}")

        if update_info["update_available"]:
            click.echo("Update available!")

            if install:
                click.echo("Installing update...")
                if update_hubqueue():
                    logger.info("HubQueue updated successfully")
                    click.echo("HubQueue updated successfully")
                else:
                    logger.error("Failed to update HubQueue")
                    click.echo("Failed to update HubQueue")
        else:
            click.echo("HubQueue is up to date")
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        click.echo(f"Error: {str(e)}")


@system.command("windows-compatibility")
@click.option("--setup", is_flag=True, help="Setup Windows environment")
def windows_compatibility(setup):
    """Check Windows compatibility."""
    logger.debug("Checking Windows compatibility")
    try:
        # Check Windows compatibility
        compatibility = check_windows_compatibility()

        if not compatibility["is_windows"]:
            logger.info("Not running on Windows")
            click.echo("Not running on Windows")
            return

        click.echo("Windows Compatibility:")
        click.echo(f"Windows Version: {compatibility['windows_version']}")
        click.echo(f"Windows Release: {compatibility['windows_release']}")
        click.echo(f"Windows Edition: {compatibility['windows_edition']}")
        click.echo(f"Running in WSL: {'Yes' if compatibility.get('is_wsl', False) else 'No'}")
        click.echo(f"Running in PowerShell: {'Yes' if compatibility.get('is_powershell', False) else 'No'}")
        click.echo(f"Running in Command Prompt: {'Yes' if compatibility.get('is_cmd', False) else 'No'}")
        click.echo(f"Git Bash Available: {'Yes' if compatibility.get('git_bash_available', False) else 'No'}")

        if setup:
            click.echo("\nSetting up Windows environment...")
            if setup_windows_environment():
                logger.info("Windows environment setup completed successfully")
                click.echo("Windows environment setup completed successfully")
            else:
                logger.error("Windows environment setup failed")
                click.echo("Windows environment setup failed")
    except Exception as e:
        logger.error(f"Error checking Windows compatibility: {str(e)}")
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
