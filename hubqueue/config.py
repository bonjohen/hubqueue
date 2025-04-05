"""
Configuration module for HubQueue.
"""
import os
import json
import shutil
import subprocess
from pathlib import Path
from .utils import get_config_dir, save_config, load_config


def get_default_editor():
    """
    Get the default text editor from environment or system.
    
    Returns:
        str: Default text editor command
    """
    # Check environment variables
    for var in ["HUBQUEUE_EDITOR", "EDITOR", "VISUAL"]:
        editor = os.environ.get(var)
        if editor:
            return editor
    
    # Check system defaults
    if os.name == "nt":  # Windows
        return "notepad.exe"
    
    # Try to find common editors on Unix-like systems
    for editor in ["nano", "vim", "vi", "emacs"]:
        if shutil.which(editor):
            return editor
    
    return "nano"  # Default to nano if nothing else is found


def get_preference(key, default=None):
    """
    Get a user preference from the config file.
    
    Args:
        key (str): Preference key
        default: Default value if preference is not set
        
    Returns:
        Value of the preference or default if not found
    """
    config = load_config()
    preferences = config.get("preferences", {})
    return preferences.get(key, default)


def set_preference(key, value):
    """
    Set a user preference in the config file.
    
    Args:
        key (str): Preference key
        value: Value to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_config()
    if "preferences" not in config:
        config["preferences"] = {}
    
    config["preferences"][key] = value
    save_config(config)
    return True


def list_preferences():
    """
    List all user preferences.
    
    Returns:
        dict: Dictionary of preferences
    """
    config = load_config()
    return config.get("preferences", {})


def get_editor():
    """
    Get the configured text editor.
    
    Returns:
        str: Text editor command
    """
    return get_preference("editor", get_default_editor())


def edit_file(file_path):
    """
    Open a file in the configured text editor.
    
    Args:
        file_path (str): Path to the file to edit
        
    Returns:
        bool: True if successful, False otherwise
    """
    editor = get_editor()
    try:
        subprocess.run([editor, file_path], check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_default_repo():
    """
    Get the default repository.
    
    Returns:
        str: Default repository in format 'owner/repo' or None
    """
    return get_preference("default_repo")


def set_default_repo(repo):
    """
    Set the default repository.
    
    Args:
        repo (str): Repository in format 'owner/repo'
        
    Returns:
        bool: True if successful, False otherwise
    """
    return set_preference("default_repo", repo)
