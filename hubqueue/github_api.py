"""
GitHub API wrapper for HubQueue.
"""
from github import Github
from github.GithubException import GithubException


class GitHubAPI:
    """Wrapper for GitHub API operations."""

    def __init__(self, token):
        """Initialize with GitHub token."""
        self.github = Github(token)

    def list_issues(self, repo_name):
        """List open issues for a repository."""
        try:
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state="open")
            return [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at,
                    "user": issue.user.login,
                    "labels": [label.name for label in issue.labels],
                }
                for issue in issues
            ]
        except GithubException as e:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            raise Exception(f"Error accessing GitHub: {str(e)}")

    def list_pull_requests(self, repo_name):
        """List open pull requests for a repository."""
        try:
            repo = self.github.get_repo(repo_name)
            pulls = repo.get_pulls(state="open")
            return [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "created_at": pr.created_at,
                    "updated_at": pr.updated_at,
                    "user": pr.user.login,
                    "branch": pr.head.ref,
                }
                for pr in pulls
            ]
        except GithubException as e:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            raise Exception(f"Error accessing GitHub: {str(e)}")

    def create_issue(self, repo_name, title, body=None, labels=None):
        """Create a new issue in the repository."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels)
            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
            }
        except GithubException as e:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            raise Exception(f"Error accessing GitHub: {str(e)}")

    def create_pull_request(self, repo_name, title, head, base, body=None):
        """Create a new pull request in the repository."""
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body, head=head, base=base)
            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
            }
        except GithubException as e:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            raise Exception(f"Error accessing GitHub: {str(e)}")
