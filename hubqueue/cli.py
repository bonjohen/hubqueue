"""
Command-line interface for HubQueue.
"""
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


if __name__ == "__main__":
    main()
