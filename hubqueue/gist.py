"""
Gist management module for HubQueue.
"""
import os
import json
from pathlib import Path
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def list_gists(public_only=False, starred=False, token=None):
    """
    List GitHub Gists for the authenticated user.
    
    Args:
        public_only (bool, optional): List only public gists. Defaults to False.
        starred (bool, optional): List starred gists instead of owned gists. Defaults to False.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of gist dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Listing {'public' if public_only else 'all'} {'starred' if starred else 'owned'} gists")
        github = Github(token)
        user = github.get_user()
        
        # Get gists
        if starred:
            gists = user.get_starred_gists()
        else:
            gists = user.get_gists()
        
        # Convert to list of dictionaries
        result = []
        for gist in gists:
            # Skip private gists if public_only is True
            if public_only and not gist.public:
                continue
                
            # Get files
            files = {}
            for filename, gist_file in gist.files.items():
                files[filename] = {
                    "filename": gist_file.filename,
                    "language": gist_file.language,
                    "size": gist_file.size,
                    "raw_url": gist_file.raw_url,
                }
            
            result.append({
                "id": gist.id,
                "description": gist.description,
                "public": gist.public,
                "created_at": gist.created_at,
                "updated_at": gist.updated_at,
                "url": gist.html_url,
                "files": files,
                "comments": gist.comments,
            })
        
        logger.info(f"Found {len(result)} gists")
        return result
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing gists: {str(e)}")
        raise Exception(f"Error listing gists: {str(e)}")


def get_gist(gist_id, token=None):
    """
    Get detailed information about a gist.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Gist information or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Get files with content
        files = {}
        for filename, gist_file in gist.files.items():
            files[filename] = {
                "filename": gist_file.filename,
                "language": gist_file.language,
                "size": gist_file.size,
                "raw_url": gist_file.raw_url,
                "content": gist_file.content,
            }
        
        # Get comments
        comments = []
        for comment in gist.get_comments():
            comments.append({
                "id": comment.id,
                "user": comment.user.login,
                "body": comment.body,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            })
        
        logger.info(f"Retrieved gist {gist_id}")
        return {
            "id": gist.id,
            "description": gist.description,
            "public": gist.public,
            "created_at": gist.created_at,
            "updated_at": gist.updated_at,
            "url": gist.html_url,
            "files": files,
            "comments": comments,
            "owner": gist.owner.login if gist.owner else None,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting gist: {str(e)}")
        raise Exception(f"Error getting gist: {str(e)}")


def create_gist(files, description="", public=False, token=None):
    """
    Create a new gist.
    
    Args:
        files (dict): Dictionary of filename to content
        description (str, optional): Gist description. Defaults to "".
        public (bool, optional): Whether the gist is public. Defaults to False.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Gist information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating {'public' if public else 'private'} gist with {len(files)} files")
        github = Github(token)
        
        # Create gist
        gist = github.get_user().create_gist(public, files, description)
        
        # Get files
        gist_files = {}
        for filename, gist_file in gist.files.items():
            gist_files[filename] = {
                "filename": gist_file.filename,
                "language": gist_file.language,
                "size": gist_file.size,
                "raw_url": gist_file.raw_url,
            }
        
        logger.info(f"Created gist {gist.id}")
        return {
            "id": gist.id,
            "description": gist.description,
            "public": gist.public,
            "created_at": gist.created_at,
            "updated_at": gist.updated_at,
            "url": gist.html_url,
            "files": gist_files,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating gist: {str(e)}")
        raise Exception(f"Error creating gist: {str(e)}")


def update_gist(gist_id, files=None, description=None, token=None):
    """
    Update an existing gist.
    
    Args:
        gist_id (str): Gist ID
        files (dict, optional): Dictionary of filename to content. Defaults to None.
        description (str, optional): New gist description. Defaults to None.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Updated gist information or None if update failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Updating gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Update gist
        if description is not None:
            gist.edit(description=description, files=files or {})
        else:
            gist.edit(files=files or {})
        
        # Get updated files
        gist_files = {}
        for filename, gist_file in gist.files.items():
            gist_files[filename] = {
                "filename": gist_file.filename,
                "language": gist_file.language,
                "size": gist_file.size,
                "raw_url": gist_file.raw_url,
            }
        
        logger.info(f"Updated gist {gist_id}")
        return {
            "id": gist.id,
            "description": gist.description,
            "public": gist.public,
            "created_at": gist.created_at,
            "updated_at": gist.updated_at,
            "url": gist.html_url,
            "files": gist_files,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error updating gist: {str(e)}")
        raise Exception(f"Error updating gist: {str(e)}")


def delete_gist(gist_id, token=None):
    """
    Delete a gist.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Delete gist
        gist.delete()
        
        logger.info(f"Deleted gist {gist_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting gist: {str(e)}")
        raise Exception(f"Error deleting gist: {str(e)}")


def star_gist(gist_id, token=None):
    """
    Star a gist.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if starring was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Starring gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Star gist
        gist.set_starred()
        
        logger.info(f"Starred gist {gist_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error starring gist: {str(e)}")
        raise Exception(f"Error starring gist: {str(e)}")


def unstar_gist(gist_id, token=None):
    """
    Unstar a gist.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if unstarring was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Unstarring gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Unstar gist
        gist.reset_starred()
        
        logger.info(f"Unstarred gist {gist_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error unstarring gist: {str(e)}")
        raise Exception(f"Error unstarring gist: {str(e)}")


def is_gist_starred(gist_id, token=None):
    """
    Check if a gist is starred by the authenticated user.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if the gist is starred, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Checking if gist {gist_id} is starred")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Check if gist is starred
        is_starred = gist.is_starred()
        
        logger.info(f"Gist {gist_id} is {'starred' if is_starred else 'not starred'}")
        return is_starred
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error checking if gist is starred: {str(e)}")
        raise Exception(f"Error checking if gist is starred: {str(e)}")


def add_gist_comment(gist_id, body, token=None):
    """
    Add a comment to a gist.
    
    Args:
        gist_id (str): Gist ID
        body (str): Comment body
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Comment information or None if addition failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Adding comment to gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Add comment
        comment = gist.create_comment(body)
        
        logger.info(f"Added comment to gist {gist_id}")
        return {
            "id": comment.id,
            "user": comment.user.login,
            "body": comment.body,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error adding comment to gist: {str(e)}")
        raise Exception(f"Error adding comment to gist: {str(e)}")


def delete_gist_comment(gist_id, comment_id, token=None):
    """
    Delete a comment from a gist.
    
    Args:
        gist_id (str): Gist ID
        comment_id (int): Comment ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting comment {comment_id} from gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Get comment
        comment = gist.get_comment(comment_id)
        
        # Delete comment
        comment.delete()
        
        logger.info(f"Deleted comment {comment_id} from gist {gist_id}")
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting comment from gist: {str(e)}")
        raise Exception(f"Error deleting comment from gist: {str(e)}")


def fork_gist(gist_id, token=None):
    """
    Fork a gist.
    
    Args:
        gist_id (str): Gist ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Forked gist information or None if forking failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Forking gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Fork gist
        forked_gist = gist.create_fork()
        
        # Get files
        gist_files = {}
        for filename, gist_file in forked_gist.files.items():
            gist_files[filename] = {
                "filename": gist_file.filename,
                "language": gist_file.language,
                "size": gist_file.size,
                "raw_url": gist_file.raw_url,
            }
        
        logger.info(f"Forked gist {gist_id} to {forked_gist.id}")
        return {
            "id": forked_gist.id,
            "description": forked_gist.description,
            "public": forked_gist.public,
            "created_at": forked_gist.created_at,
            "updated_at": forked_gist.updated_at,
            "url": forked_gist.html_url,
            "files": gist_files,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error forking gist: {str(e)}")
        raise Exception(f"Error forking gist: {str(e)}")


def download_gist(gist_id, directory=None, token=None):
    """
    Download a gist to the local filesystem.
    
    Args:
        gist_id (str): Gist ID
        directory (str, optional): Directory to save files to. If None, uses current directory.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of downloaded file paths or None if download failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Downloading gist {gist_id}")
        github = Github(token)
        
        # Get gist
        gist = github.get_gist(gist_id)
        
        # Create directory if it doesn't exist
        if directory:
            os.makedirs(directory, exist_ok=True)
        else:
            directory = "."
        
        # Download files
        downloaded_files = []
        for filename, gist_file in gist.files.items():
            # Create file path
            file_path = os.path.join(directory, filename)
            
            # Write file content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(gist_file.content)
            
            downloaded_files.append(file_path)
        
        logger.info(f"Downloaded {len(downloaded_files)} files from gist {gist_id}")
        return downloaded_files
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error downloading gist: {str(e)}")
        raise Exception(f"Error downloading gist: {str(e)}")


def upload_gist(files_or_directory, description="", public=False, token=None):
    """
    Upload files to a new gist.
    
    Args:
        files_or_directory (str or list): Path to directory or list of file paths
        description (str, optional): Gist description. Defaults to "".
        public (bool, optional): Whether the gist is public. Defaults to False.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Gist information or None if upload failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Uploading files to a new gist")
        
        # Determine files to upload
        file_paths = []
        if isinstance(files_or_directory, str):
            # Check if it's a directory
            if os.path.isdir(files_or_directory):
                # Get all files in directory
                for root, _, files in os.walk(files_or_directory):
                    for file in files:
                        file_paths.append(os.path.join(root, file))
            else:
                # Single file
                file_paths.append(files_or_directory)
        else:
            # List of files
            file_paths = files_or_directory
        
        # Read file contents
        files_dict = {}
        for file_path in file_paths:
            # Skip directories
            if os.path.isdir(file_path):
                continue
                
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Use filename as key
            filename = os.path.basename(file_path)
            files_dict[filename] = content
        
        if not files_dict:
            logger.error("No files to upload")
            raise ValueError("No files to upload")
        
        # Create gist
        return create_gist(files_dict, description, public, token)
    except Exception as e:
        logger.error(f"Error uploading files to gist: {str(e)}")
        raise Exception(f"Error uploading files to gist: {str(e)}")
