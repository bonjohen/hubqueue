"""
Utility functions for HubQueue.
"""
import os
import json
from pathlib import Path


def get_config_dir():
    """Get the configuration directory for HubQueue."""
    config_dir = Path.home() / ".hubqueue"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def save_config(config_data):
    """Save configuration data to the config file."""
    config_file = get_config_dir() / "config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)


def load_config():
    """Load configuration data from the config file."""
    config_file = get_config_dir() / "config.json"
    if not config_file.exists():
        return {}
    
    with open(config_file, "r") as f:
        return json.load(f)


def get_github_token():
    """Get GitHub token from environment or config file."""
    # First check environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # Then check config file
    config = load_config()
    return config.get("github_token")
