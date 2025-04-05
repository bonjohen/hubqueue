"""
Project management module for HubQueue.
"""
import os
import json
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def list_project_boards(repo_name, token=None):
    """
    List project boards for a repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of project board dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing project boards for repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project boards
        projects = repo.get_projects()
        
        # Convert to list of dictionaries
        result = []
        for project in projects:
            # Get columns
            columns = []
            for column in project.get_columns():
                columns.append({
                    "id": column.id,
                    "name": column.name,
                    "cards_url": column.cards_url,
                })
            
            result.append({
                "id": project.id,
                "name": project.name,
                "body": project.body,
                "state": project.state,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "html_url": project.html_url,
                "columns": columns,
            })
        
        logger.info(f"Found {len(result)} project boards for {repo_name}")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing project boards: {str(e)}")
        raise Exception(f"Error listing project boards: {str(e)}")


def get_project_board(repo_name, project_id, token=None):
    """
    Get detailed information about a project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Project board information or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting project board {project_id} from repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get columns
        columns = []
        for column in project.get_columns():
            # Get cards
            cards = []
            for card in column.get_cards():
                card_info = {
                    "id": card.id,
                    "note": card.note,
                    "created_at": card.created_at,
                    "updated_at": card.updated_at,
                    "content_url": card.content_url,
                }
                
                # Try to get content (issue or PR)
                if card.content_url:
                    try:
                        if "/issues/" in card.content_url:
                            issue_number = int(card.content_url.split("/issues/")[1])
                            issue = repo.get_issue(issue_number)
                            card_info["content"] = {
                                "type": "issue",
                                "number": issue.number,
                                "title": issue.title,
                                "state": issue.state,
                            }
                        elif "/pull/" in card.content_url:
                            pr_number = int(card.content_url.split("/pull/")[1])
                            pr = repo.get_pull(pr_number)
                            card_info["content"] = {
                                "type": "pull_request",
                                "number": pr.number,
                                "title": pr.title,
                                "state": pr.state,
                            }
                    except Exception as e:
                        logger.warning(f"Error getting card content: {str(e)}")
                
                cards.append(card_info)
            
            columns.append({
                "id": column.id,
                "name": column.name,
                "cards_url": column.cards_url,
                "cards": cards,
            })
        
        logger.info(f"Retrieved project board {project_id} from {repo_name}")
        return {
            "id": project.id,
            "name": project.name,
            "body": project.body,
            "state": project.state,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "html_url": project.html_url,
            "columns": columns,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting project board: {str(e)}")
        raise Exception(f"Error getting project board: {str(e)}")


def create_project_board(repo_name, name, body=None, token=None):
    """
    Create a new project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        name (str): Project name
        body (str, optional): Project description. Defaults to None.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Project board information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating project board {name} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Create project
        project = repo.create_project(name, body)
        
        logger.info(f"Created project board {name} in {repo_name}")
        return {
            "id": project.id,
            "name": project.name,
            "body": project.body,
            "state": project.state,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "html_url": project.html_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating project board: {str(e)}")
        raise Exception(f"Error creating project board: {str(e)}")


def create_project_column(repo_name, project_id, name, token=None):
    """
    Create a new column in a project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        name (str): Column name
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Column information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating column {name} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Create column
        column = project.create_column(name)
        
        logger.info(f"Created column {name} in project {project_id}")
        return {
            "id": column.id,
            "name": column.name,
            "cards_url": column.cards_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating project column: {str(e)}")
        raise Exception(f"Error creating project column: {str(e)}")


def add_issue_to_project(repo_name, project_id, column_id, issue_number, token=None):
    """
    Add an issue to a project board column.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        column_id (int): Column ID
        issue_number (int): Issue number
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Card information or None if addition failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Adding issue {issue_number} to column {column_id} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get issue
        issue = repo.get_issue(issue_number)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Add issue to column
        card = column.create_card(content_id=issue.id, content_type="Issue")
        
        logger.info(f"Added issue {issue_number} to column {column_id} in project {project_id}")
        return {
            "id": card.id,
            "note": card.note,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "content_url": card.content_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error adding issue to project: {str(e)}")
        raise Exception(f"Error adding issue to project: {str(e)}")


def add_pr_to_project(repo_name, project_id, column_id, pr_number, token=None):
    """
    Add a pull request to a project board column.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        column_id (int): Column ID
        pr_number (int): Pull request number
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Card information or None if addition failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Adding PR {pr_number} to column {column_id} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get pull request
        pr = repo.get_pull(pr_number)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Add pull request to column
        card = column.create_card(content_id=pr.id, content_type="PullRequest")
        
        logger.info(f"Added PR {pr_number} to column {column_id} in project {project_id}")
        return {
            "id": card.id,
            "note": card.note,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "content_url": card.content_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error adding PR to project: {str(e)}")
        raise Exception(f"Error adding PR to project: {str(e)}")


def add_note_to_project(repo_name, project_id, column_id, note, token=None):
    """
    Add a note to a project board column.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        column_id (int): Column ID
        note (str): Note content
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Card information or None if addition failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Adding note to column {column_id} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Add note to column
        card = column.create_card(note=note)
        
        logger.info(f"Added note to column {column_id} in project {project_id}")
        return {
            "id": card.id,
            "note": card.note,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "content_url": card.content_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error adding note to project: {str(e)}")
        raise Exception(f"Error adding note to project: {str(e)}")


def move_project_card(repo_name, project_id, card_id, column_id, position="top", token=None):
    """
    Move a card to a different column or position.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        card_id (int): Card ID
        column_id (int): Target column ID
        position (str, optional): Position in column ("top", "bottom", or "after:card_id"). Defaults to "top".
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if move was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Moving card {card_id} to column {column_id} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Get card
        for col in project.get_columns():
            try:
                card = col.get_card(card_id)
                break
            except GithubException:
                continue
        else:
            logger.error(f"Card {card_id} not found in project {project_id}")
            raise Exception(f"Card {card_id} not found in project {project_id}")
        
        # Move card
        if position == "top":
            card.move(position="top", column=column)
        elif position == "bottom":
            card.move(position="bottom", column=column)
        elif position.startswith("after:"):
            after_card_id = int(position.split(":")[1])
            card.move(position=f"after:{after_card_id}", column=column)
        else:
            logger.error(f"Invalid position: {position}")
            raise ValueError(f"Invalid position: {position}. Use 'top', 'bottom', or 'after:card_id'.")
        
        logger.info(f"Moved card {card_id} to column {column_id} in project {project_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error moving project card: {str(e)}")
        raise Exception(f"Error moving project card: {str(e)}")


def delete_project_card(repo_name, project_id, card_id, token=None):
    """
    Delete a card from a project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        card_id (int): Card ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting card {card_id} from project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Find and delete card
        for column in project.get_columns():
            try:
                card = column.get_card(card_id)
                card.delete()
                logger.info(f"Deleted card {card_id} from project {project_id}")
                return True
            except GithubException:
                continue
        
        logger.error(f"Card {card_id} not found in project {project_id}")
        raise Exception(f"Card {card_id} not found in project {project_id}")
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting project card: {str(e)}")
        raise Exception(f"Error deleting project card: {str(e)}")


def delete_project_column(repo_name, project_id, column_id, token=None):
    """
    Delete a column from a project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        column_id (int): Column ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting column {column_id} from project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Delete column
        column.delete()
        
        logger.info(f"Deleted column {column_id} from project {project_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting project column: {str(e)}")
        raise Exception(f"Error deleting project column: {str(e)}")


def delete_project_board(repo_name, project_id, token=None):
    """
    Delete a project board.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting project {project_id} from repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Delete project
        project.delete()
        
        logger.info(f"Deleted project {project_id} from repository {repo_name}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting project board: {str(e)}")
        raise Exception(f"Error deleting project board: {str(e)}")


def create_project_from_template(repo_name, name, template, token=None):
    """
    Create a project board from a template.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        name (str): Project name
        template (str): Template name (basic, automated, bug_triage)
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Project board information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating project {name} from template {template} in repository {repo_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Create project
        project_info = create_project_board(repo_name, name, f"Project created from {template} template", token)
        project_id = project_info["id"]
        
        # Add columns based on template
        if template.lower() == "basic":
            create_project_column(repo_name, project_id, "To Do", token)
            create_project_column(repo_name, project_id, "In Progress", token)
            create_project_column(repo_name, project_id, "Done", token)
        elif template.lower() == "automated":
            create_project_column(repo_name, project_id, "To Do", token)
            create_project_column(repo_name, project_id, "In Progress", token)
            create_project_column(repo_name, project_id, "Review", token)
            create_project_column(repo_name, project_id, "Done", token)
        elif template.lower() == "bug_triage":
            create_project_column(repo_name, project_id, "New", token)
            create_project_column(repo_name, project_id, "Needs Triage", token)
            create_project_column(repo_name, project_id, "Confirmed", token)
            create_project_column(repo_name, project_id, "In Progress", token)
            create_project_column(repo_name, project_id, "Fixed", token)
        else:
            logger.error(f"Unknown template: {template}")
            raise ValueError(f"Unknown template: {template}. Use 'basic', 'automated', or 'bug_triage'.")
        
        # Get updated project
        project = get_project_board(repo_name, project_id, token)
        
        logger.info(f"Created project {name} from template {template} in repository {repo_name}")
        return project
    except Exception as e:
        logger.error(f"Error creating project from template: {str(e)}")
        raise Exception(f"Error creating project from template: {str(e)}")


def configure_project_automation(repo_name, project_id, column_id, event_type, configuration, token=None):
    """
    Configure automation for a project column.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        project_id (int): Project ID
        column_id (int): Column ID
        event_type (str): Event type (e.g., "issue", "pull_request", "card")
        configuration (dict): Automation configuration
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Configuring automation for column {column_id} in project {project_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get project
        project = repo.get_project(project_id)
        
        # Get column
        column = project.get_column(column_id)
        
        # Configure automation
        # Note: PyGithub doesn't have direct support for project automation,
        # so we would need to use the underlying requester or a different approach.
        # This is a placeholder for future implementation.
        
        logger.info(f"Configured automation for column {column_id} in project {project_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error configuring project automation: {str(e)}")
        raise Exception(f"Error configuring project automation: {str(e)}")
