"""
Issue and Pull Request management module for HubQueue.
"""
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def list_issues(repo_name, state="open", labels=None, assignee=None, token=None):
    """
    List issues for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        state (str, optional): Issue state (open, closed, all). Defaults to "open".
        labels (list, optional): List of label names to filter by.
        assignee (str, optional): GitHub username to filter by assignee.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of issue dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing issues for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Build filter parameters
        params = {"state": state}
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
        
        # Get issues
        issues = repo.get_issues(**params)
        
        # Convert to list of dictionaries
        result = []
        for issue in issues:
            # Skip pull requests (they are also returned as issues by the API)
            if issue.pull_request is not None:
                continue
                
            result.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
                "html_url": issue.html_url,
                "body": issue.body,
                "user": issue.user.login,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "comments": issue.comments,
            })
        
        logger.info(f"Found {len(result)} issues for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing issues: {str(e)}")
        raise Exception(f"Error listing issues: {str(e)}")


def create_issue(repo_name, title, body=None, labels=None, assignees=None, token=None):
    """
    Create a new issue in a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        title (str): Issue title
        body (str, optional): Issue body
        labels (list, optional): List of label names to apply
        assignees (list, optional): List of GitHub usernames to assign
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Issue information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating issue in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Create issue
        issue = repo.create_issue(
            title=title,
            body=body,
            labels=labels,
            assignees=assignees
        )
        
        logger.info(f"Created issue #{issue.number} in {repo_name}")
        return {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "created_at": issue.created_at,
            "html_url": issue.html_url,
            "body": issue.body,
            "user": issue.user.login,
            "labels": [label.name for label in issue.labels],
            "assignees": [assignee.login for assignee in issue.assignees],
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating issue: {str(e)}")
        raise Exception(f"Error creating issue: {str(e)}")


def list_pull_requests(repo_name, state="open", base=None, head=None, token=None):
    """
    List pull requests for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        state (str, optional): PR state (open, closed, all). Defaults to "open".
        base (str, optional): Filter by base branch name.
        head (str, optional): Filter by head branch name.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of pull request dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing pull requests for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Build filter parameters
        params = {"state": state}
        if base:
            params["base"] = base
        if head:
            params["head"] = head
        
        # Get pull requests
        pulls = repo.get_pulls(**params)
        
        # Convert to list of dictionaries
        result = []
        for pr in pulls:
            result.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at,
                "html_url": pr.html_url,
                "body": pr.body,
                "user": pr.user.login,
                "base": pr.base.ref,
                "head": pr.head.ref,
                "mergeable": pr.mergeable,
                "merged": pr.merged,
                "comments": pr.comments,
                "review_comments": pr.review_comments,
                "commits": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
            })
        
        logger.info(f"Found {len(result)} pull requests for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing pull requests: {str(e)}")
        raise Exception(f"Error listing pull requests: {str(e)}")


def checkout_pull_request(repo_name, pr_number, directory=".", token=None):
    """
    Checkout a pull request locally for review.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        pr_number (int): Pull request number
        directory (str, optional): Repository directory. Defaults to current directory.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Pull request information or None if checkout failed
    """
    import subprocess
    import os
    
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Checking out pull request #{pr_number} from {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get pull request
        pr = repo.get_pull(pr_number)
        
        # Check if directory is a git repository
        git_dir = os.path.join(directory, ".git")
        if not os.path.isdir(git_dir):
            logger.error(f"Directory {directory} is not a git repository")
            raise Exception(f"Directory {directory} is not a git repository")
        
        # Fetch the pull request
        fetch_command = [
            "git", "fetch", "origin", 
            f"pull/{pr_number}/head:pr-{pr_number}"
        ]
        subprocess.run(
            fetch_command,
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Checkout the branch
        checkout_command = ["git", "checkout", f"pr-{pr_number}"]
        subprocess.run(
            checkout_command,
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Checked out pull request #{pr_number} to branch pr-{pr_number}")
        return {
            "number": pr.number,
            "title": pr.title,
            "branch": f"pr-{pr_number}",
            "base": pr.base.ref,
            "head": pr.head.ref,
            "user": pr.user.login,
            "html_url": pr.html_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        raise Exception(f"Git command failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Error checking out pull request: {str(e)}")
        raise Exception(f"Error checking out pull request: {str(e)}")


def get_issue(repo_name, issue_number, token=None):
    """
    Get detailed information about an issue.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        issue_number (int): Issue number
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Issue information or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting issue #{issue_number} from {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get issue
        issue = repo.get_issue(issue_number)
        
        # Skip if it's a pull request
        if issue.pull_request is not None:
            logger.warning(f"Issue #{issue_number} is a pull request")
            raise Exception(f"Issue #{issue_number} is a pull request, not an issue")
        
        # Get comments
        comments = []
        for comment in issue.get_comments():
            comments.append({
                "id": comment.id,
                "user": comment.user.login,
                "body": comment.body,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            })
        
        logger.info(f"Retrieved issue #{issue_number} from {repo_name}")
        return {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "html_url": issue.html_url,
            "body": issue.body,
            "user": issue.user.login,
            "labels": [label.name for label in issue.labels],
            "assignees": [assignee.login for assignee in issue.assignees],
            "comments": comments,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting issue: {str(e)}")
        raise Exception(f"Error getting issue: {str(e)}")


def get_pull_request(repo_name, pr_number, token=None):
    """
    Get detailed information about a pull request.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        pr_number (int): Pull request number
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Pull request information or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting pull request #{pr_number} from {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get pull request
        pr = repo.get_pull(pr_number)
        
        # Get comments
        comments = []
        for comment in pr.get_issue_comments():
            comments.append({
                "id": comment.id,
                "user": comment.user.login,
                "body": comment.body,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            })
        
        # Get review comments
        review_comments = []
        for comment in pr.get_review_comments():
            review_comments.append({
                "id": comment.id,
                "user": comment.user.login,
                "body": comment.body,
                "path": comment.path,
                "position": comment.position,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            })
        
        # Get commits
        commits = []
        for commit in pr.get_commits():
            commits.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date,
            })
        
        logger.info(f"Retrieved pull request #{pr_number} from {repo_name}")
        return {
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "html_url": pr.html_url,
            "body": pr.body,
            "user": pr.user.login,
            "base": pr.base.ref,
            "head": pr.head.ref,
            "mergeable": pr.mergeable,
            "merged": pr.merged,
            "comments": comments,
            "review_comments": review_comments,
            "commits": commits,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting pull request: {str(e)}")
        raise Exception(f"Error getting pull request: {str(e)}")
