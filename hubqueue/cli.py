"""
Command-line interface for HubQueue.
"""
import os
import click
import webbrowser
from dotenv import load_dotenv
from tabulate import tabulate
from . import __version__
from .github_api import GitHubAPI
from .auth import (
    get_github_token, validate_token, save_token,
    clear_token, get_user_info, start_oauth_flow,
    complete_oauth_flow
)
from .config import (
    get_preference, set_preference, list_preferences,
    get_editor, edit_file, get_default_repo, set_default_repo
)

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version=__version__)
def main():
    """HubQueue - A command-line interface for GitHub tools."""
    pass


# Authentication commands group
@main.group()
def auth():
    """Authentication commands for GitHub."""
    pass


@auth.command()
@click.option("--token", prompt=True, hide_input=True, help="GitHub API token")
def login(token):
    """Login with GitHub token."""
    if validate_token(token):
        save_token(token)
        user_info = get_user_info(token)
        click.echo(f"Successfully logged in as {user_info['login']}")
    else:
        click.echo("Error: Invalid GitHub token")


@auth.command()
def logout():
    """Logout and remove stored GitHub token."""
    if clear_token():
        click.echo("Successfully logged out")
    else:
        click.echo("No token found")


@auth.command()
def status():
    """Check authentication status."""
    token = get_github_token()
    if not token:
        click.echo("Not logged in")
        return

    if validate_token(token):
        user_info = get_user_info(token)
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


@main.command()
@click.option("--repo", help="Repository name in format 'owner/repo'")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_issues(repo, token):
    """List open issues for a repository."""
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not repo:
        click.echo("Error: Repository not specified. Use --repo option.")
        return

    try:
        github_api = GitHubAPI(token)
        issues = github_api.list_issues(repo)

        if not issues:
            click.echo(f"No open issues found for {repo}")
            return

        click.echo(f"Open issues for {repo}:")
        for issue in issues:
            click.echo(f"#{issue['number']} - {issue['title']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@main.command()
@click.option("--repo", help="Repository name in format 'owner/repo'")
@click.option("--token", help="GitHub API token (or set GITHUB_TOKEN env variable)")
def list_prs(repo, token):
    """List open pull requests for a repository."""
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        click.echo("Error: GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable.")
        return

    if not repo:
        click.echo("Error: Repository not specified. Use --repo option.")
        return

    try:
        github_api = GitHubAPI(token)
        prs = github_api.list_pull_requests(repo)

        if not prs:
            click.echo(f"No open pull requests found for {repo}")
            return

        click.echo(f"Open pull requests for {repo}:")
        for pr in prs:
            click.echo(f"#{pr['number']} - {pr['title']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
