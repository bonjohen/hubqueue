"""
Authentication module for HubQueue.
"""
import os
import json
import webbrowser
from pathlib import Path
import requests
from github import Github
from github.GithubException import BadCredentialsException
from .utils import get_config_dir, save_config, load_config


def get_github_token():
    """
    Get GitHub token from environment or config file.
    
    Returns:
        str: GitHub token or None if not found
    """
    # First check environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # Then check config file
    config = load_config()
    return config.get("github_token")


def validate_token(token):
    """
    Validate GitHub token by making a test API call.
    
    Args:
        token (str): GitHub token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token:
        return False
        
    try:
        github = Github(token)
        # Try to get the authenticated user to validate token
        user = github.get_user()
        _ = user.login  # This will trigger an API call
        return True
    except BadCredentialsException:
        return False
    except Exception:
        return False


def save_token(token):
    """
    Save GitHub token to config file.
    
    Args:
        token (str): GitHub token to save
    """
    config = load_config()
    config["github_token"] = token
    save_config(config)


def clear_token():
    """
    Remove GitHub token from config file.
    
    Returns:
        bool: True if token was removed, False if no token was found
    """
    config = load_config()
    if "github_token" in config:
        del config["github_token"]
        save_config(config)
        return True
    return False


def start_oauth_flow(client_id, redirect_uri="http://localhost:8000"):
    """
    Start OAuth flow to get GitHub token.
    
    Args:
        client_id (str): GitHub OAuth client ID
        redirect_uri (str): Redirect URI for OAuth flow
        
    Returns:
        str: Authorization URL to open in browser
    """
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=repo,user,gist"
    )
    return auth_url


def complete_oauth_flow(code, client_id, client_secret):
    """
    Complete OAuth flow by exchanging code for token.
    
    Args:
        code (str): Authorization code from GitHub
        client_id (str): GitHub OAuth client ID
        client_secret (str): GitHub OAuth client secret
        
    Returns:
        str: GitHub token or None if exchange failed
    """
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
        headers={"Accept": "application/json"},
    )
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            token = data["access_token"]
            save_token(token)
            return token
    
    return None


def get_user_info(token=None):
    """
    Get information about the authenticated user.
    
    Args:
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: User information or None if token is invalid
    """
    token = token or get_github_token()
    if not token:
        return None
        
    try:
        github = Github(token)
        user = github.get_user()
        return {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "html_url": user.html_url,
            "public_repos": user.public_repos,
            "private_repos": user.total_private_repos,
        }
    except Exception:
        return None
