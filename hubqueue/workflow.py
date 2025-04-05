"""
Workflow automation and monitoring module for HubQueue.
"""
import os
import time
import json
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def list_workflows(repo_name, token=None):
    """
    List GitHub Actions workflows for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of workflow dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing workflows for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflows
        workflows = repo.get_workflows()
        
        # Convert to list of dictionaries
        result = []
        for workflow in workflows:
            result.append({
                "id": workflow.id,
                "name": workflow.name,
                "path": workflow.path,
                "state": workflow.state,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at,
                "url": workflow.html_url,
            })
        
        logger.info(f"Found {len(result)} workflows for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise Exception(f"Error listing workflows: {str(e)}")


def trigger_workflow(repo_name, workflow_id, ref="main", inputs=None, token=None):
    """
    Trigger a GitHub Actions workflow run.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        workflow_id (str): Workflow ID or file name
        ref (str, optional): Git reference (branch, tag, SHA). Defaults to "main".
        inputs (dict, optional): Workflow inputs. Defaults to None.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Workflow run information or None if triggering failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Triggering workflow {workflow_id} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflow
        workflow = None
        try:
            # Try to get by ID
            workflow = repo.get_workflow(workflow_id)
        except Exception:
            # Try to get by file name
            workflows = repo.get_workflows()
            for wf in workflows:
                if wf.path.endswith(workflow_id):
                    workflow = wf
                    break
        
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            raise Exception(f"Workflow {workflow_id} not found")
        
        # Trigger workflow
        run = workflow.create_dispatch(ref, inputs or {})
        
        logger.info(f"Triggered workflow {workflow.name} in {repo_name}")
        return {
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "run_id": run.id if hasattr(run, "id") else None,
            "status": "queued",
            "url": workflow.html_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error triggering workflow: {str(e)}")
        raise Exception(f"Error triggering workflow: {str(e)}")


def list_workflow_runs(repo_name, workflow_id=None, status=None, branch=None, token=None):
    """
    List GitHub Actions workflow runs for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        workflow_id (str, optional): Filter by workflow ID or file name. Defaults to None.
        status (str, optional): Filter by status (queued, in_progress, completed, etc.). Defaults to None.
        branch (str, optional): Filter by branch name. Defaults to None.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of workflow run dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing workflow runs for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflow if specified
        workflow = None
        if workflow_id:
            try:
                # Try to get by ID
                workflow = repo.get_workflow(workflow_id)
            except Exception:
                # Try to get by file name
                workflows = repo.get_workflows()
                for wf in workflows:
                    if wf.path.endswith(workflow_id):
                        workflow = wf
                        break
            
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                raise Exception(f"Workflow {workflow_id} not found")
        
        # Get workflow runs
        if workflow:
            runs = workflow.get_runs()
        else:
            runs = repo.get_workflow_runs()
        
        # Filter runs
        result = []
        for run in runs:
            # Filter by status
            if status and run.status != status:
                continue
            
            # Filter by branch
            if branch and run.head_branch != branch:
                continue
            
            result.append({
                "id": run.id,
                "name": run.name,
                "workflow_id": run.workflow_id,
                "status": run.status,
                "conclusion": run.conclusion,
                "branch": run.head_branch,
                "commit": run.head_sha,
                "created_at": run.created_at,
                "updated_at": run.updated_at,
                "url": run.html_url,
            })
        
        logger.info(f"Found {len(result)} workflow runs for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing workflow runs: {str(e)}")
        raise Exception(f"Error listing workflow runs: {str(e)}")


def get_workflow_run(repo_name, run_id, token=None):
    """
    Get detailed information about a workflow run.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        run_id (int): Workflow run ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Workflow run information or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting workflow run {run_id} from repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflow run
        run = repo.get_workflow_run(run_id)
        
        # Get jobs
        jobs = []
        for job in run.get_jobs():
            steps = []
            for step in job.get_steps():
                steps.append({
                    "name": step.name,
                    "status": step.status,
                    "conclusion": step.conclusion,
                    "number": step.number,
                    "started_at": step.started_at,
                    "completed_at": step.completed_at,
                })
            
            jobs.append({
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "conclusion": job.conclusion,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "steps": steps,
            })
        
        logger.info(f"Retrieved workflow run {run_id} from {repo_name}")
        return {
            "id": run.id,
            "name": run.name,
            "workflow_id": run.workflow_id,
            "status": run.status,
            "conclusion": run.conclusion,
            "branch": run.head_branch,
            "commit": run.head_sha,
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "url": run.html_url,
            "jobs": jobs,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting workflow run: {str(e)}")
        raise Exception(f"Error getting workflow run: {str(e)}")


def monitor_workflow_run(repo_name, run_id, interval=5, timeout=300, token=None):
    """
    Monitor a workflow run until completion or timeout.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        run_id (int): Workflow run ID
        interval (int, optional): Polling interval in seconds. Defaults to 5.
        timeout (int, optional): Timeout in seconds. Defaults to 300.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Final workflow run information or None if monitoring failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Monitoring workflow run {run_id} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Monitor workflow run
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Get workflow run
            run = repo.get_workflow_run(run_id)
            
            # Check if run is complete
            if run.status == "completed":
                logger.info(f"Workflow run {run_id} completed with conclusion: {run.conclusion}")
                return {
                    "id": run.id,
                    "name": run.name,
                    "workflow_id": run.workflow_id,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "branch": run.head_branch,
                    "commit": run.head_sha,
                    "created_at": run.created_at,
                    "updated_at": run.updated_at,
                    "url": run.html_url,
                }
            
            # Wait for next check
            logger.debug(f"Workflow run {run_id} status: {run.status}")
            time.sleep(interval)
        
        # Timeout
        logger.warning(f"Monitoring workflow run {run_id} timed out after {timeout} seconds")
        return {
            "id": run.id,
            "name": run.name,
            "workflow_id": run.workflow_id,
            "status": run.status,
            "conclusion": None,
            "branch": run.head_branch,
            "commit": run.head_sha,
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "url": run.html_url,
            "timed_out": True,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error monitoring workflow run: {str(e)}")
        raise Exception(f"Error monitoring workflow run: {str(e)}")


def cancel_workflow_run(repo_name, run_id, token=None):
    """
    Cancel a workflow run.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        run_id (int): Workflow run ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if cancellation was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Cancelling workflow run {run_id} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflow run
        run = repo.get_workflow_run(run_id)
        
        # Cancel workflow run
        run.cancel()
        
        logger.info(f"Cancelled workflow run {run_id} in {repo_name}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error cancelling workflow run: {str(e)}")
        raise Exception(f"Error cancelling workflow run: {str(e)}")


def rerun_workflow_run(repo_name, run_id, token=None):
    """
    Rerun a workflow run.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        run_id (int): Workflow run ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if rerun was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Rerunning workflow run {run_id} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get workflow run
        run = repo.get_workflow_run(run_id)
        
        # Rerun workflow run
        run.rerun()
        
        logger.info(f"Reran workflow run {run_id} in {repo_name}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error rerunning workflow run: {str(e)}")
        raise Exception(f"Error rerunning workflow run: {str(e)}")


def list_repository_secrets(repo_name, token=None):
    """
    List repository secrets.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of secret dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing secrets for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get secrets
        secrets = repo.get_secrets()
        
        # Convert to list of dictionaries
        result = []
        for secret in secrets:
            result.append({
                "name": secret.name,
                "created_at": secret.created_at,
                "updated_at": secret.updated_at,
            })
        
        logger.info(f"Found {len(result)} secrets for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing secrets: {str(e)}")
        raise Exception(f"Error listing secrets: {str(e)}")


def create_repository_secret(repo_name, secret_name, secret_value, token=None):
    """
    Create or update a repository secret.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        secret_name (str): Secret name
        secret_value (str): Secret value
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if creation was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Creating/updating secret {secret_name} for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Create or update secret
        repo.create_secret(secret_name, secret_value)
        
        logger.info(f"Created/updated secret {secret_name} for {repo_name}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating/updating secret: {str(e)}")
        raise Exception(f"Error creating/updating secret: {str(e)}")


def delete_repository_secret(repo_name, secret_name, token=None):
    """
    Delete a repository secret.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        secret_name (str): Secret name
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting secret {secret_name} from repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Delete secret
        repo.delete_secret(secret_name)
        
        logger.info(f"Deleted secret {secret_name} from {repo_name}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting secret: {str(e)}")
        raise Exception(f"Error deleting secret: {str(e)}")


def list_workflow_caches(repo_name, token=None):
    """
    List GitHub Actions caches for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of cache dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing workflow caches for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get caches
        # Note: PyGithub doesn't have direct support for caches API, so we use the underlying requester
        url = f"/repos/{repo_name}/actions/caches"
        response = github._Github__requester.requestJson("GET", url)[0]
        
        # Convert to list of dictionaries
        result = []
        for cache in response.get("actions_caches", []):
            result.append({
                "id": cache.get("id"),
                "ref": cache.get("ref"),
                "key": cache.get("key"),
                "version": cache.get("version"),
                "size": cache.get("size_in_bytes"),
                "created_at": cache.get("created_at"),
            })
        
        logger.info(f"Found {len(result)} workflow caches for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing workflow caches: {str(e)}")
        raise Exception(f"Error listing workflow caches: {str(e)}")


def delete_workflow_cache(repo_name, cache_id=None, cache_key=None, token=None):
    """
    Delete a GitHub Actions cache.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        cache_id (str, optional): Cache ID to delete. Defaults to None.
        cache_key (str, optional): Cache key to delete. Defaults to None.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    if not cache_id and not cache_key:
        logger.error("Either cache_id or cache_key must be provided")
        raise ValueError("Either cache_id or cache_key must be provided")
    
    try:
        logger.debug(f"Deleting workflow cache from repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Delete cache
        # Note: PyGithub doesn't have direct support for caches API, so we use the underlying requester
        if cache_id:
            url = f"/repos/{repo_name}/actions/caches/{cache_id}"
            github._Github__requester.requestJson("DELETE", url)
            logger.info(f"Deleted workflow cache {cache_id} from {repo_name}")
        else:
            url = f"/repos/{repo_name}/actions/caches"
            params = {"key": cache_key}
            github._Github__requester.requestJson("DELETE", url, params=params)
            logger.info(f"Deleted workflow cache with key {cache_key} from {repo_name}")
        
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting workflow cache: {str(e)}")
        raise Exception(f"Error deleting workflow cache: {str(e)}")
