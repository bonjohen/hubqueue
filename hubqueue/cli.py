"""
Command-line interface for HubQueue.
"""
import os
import click
from dotenv import load_dotenv
from . import __version__
from .github_api import GitHubAPI

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version=__version__)
def main():
    """HubQueue - A command-line interface for GitHub tools."""
    pass


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
