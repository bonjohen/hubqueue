"""
SSH key management module for HubQueue.
"""
import os
import re
import json
import subprocess
import tempfile
from pathlib import Path
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()

# Default SSH key directory
DEFAULT_SSH_DIR = os.path.join(os.path.expanduser("~"), ".ssh")


def list_ssh_keys(token=None):
    """
    List SSH keys for the authenticated user on GitHub.
    
    Args:
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of SSH key dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug("Listing SSH keys")
        github = Github(token)
        user = github.get_user()
        
        # Get SSH keys
        keys = []
        for key in user.get_keys():
            keys.append({
                "id": key.id,
                "title": key.title,
                "key": key.key,
                "url": key.url,
                "created_at": key.created_at,
                "verified": key.verified,
            })
        
        logger.info(f"Found {len(keys)} SSH keys")
        return keys
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing SSH keys: {str(e)}")
        raise Exception(f"Error listing SSH keys: {str(e)}")


def list_local_ssh_keys(ssh_dir=None):
    """
    List SSH keys in the local .ssh directory.
    
    Args:
        ssh_dir (str, optional): SSH directory. If None, uses default.
        
    Returns:
        list: List of SSH key dictionaries
    """
    ssh_dir = ssh_dir or DEFAULT_SSH_DIR
    
    try:
        logger.debug(f"Listing local SSH keys in {ssh_dir}")
        
        # Create SSH directory if it doesn't exist
        os.makedirs(ssh_dir, exist_ok=True)
        
        # List files in SSH directory
        keys = []
        for file in os.listdir(ssh_dir):
            file_path = os.path.join(ssh_dir, file)
            
            # Skip directories and non-regular files
            if not os.path.isfile(file_path):
                continue
            
            # Check if file is a private key
            is_private_key = file.endswith(".pem") or file.endswith(".key") or (
                not file.endswith(".pub") and not file.startswith("known_hosts") and
                not file.startswith("authorized_keys") and not file.startswith("config")
            )
            
            # Check if file is a public key
            is_public_key = file.endswith(".pub")
            
            if is_private_key or is_public_key:
                # Get key type and fingerprint
                key_type = None
                fingerprint = None
                
                if is_public_key:
                    # Read public key
                    with open(file_path, "r") as f:
                        content = f.read().strip()
                        parts = content.split()
                        if len(parts) >= 2:
                            key_type = parts[0]
                            
                            # Get fingerprint
                            try:
                                result = subprocess.run(
                                    ["ssh-keygen", "-lf", file_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                                )
                                if result.returncode == 0:
                                    fingerprint = result.stdout.strip().split()[1]
                            except Exception:
                                pass
                
                keys.append({
                    "file": file,
                    "path": file_path,
                    "type": "private" if is_private_key else "public",
                    "key_type": key_type,
                    "fingerprint": fingerprint,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path),
                })
        
        logger.info(f"Found {len(keys)} local SSH keys")
        return keys
    except Exception as e:
        logger.error(f"Error listing local SSH keys: {str(e)}")
        raise Exception(f"Error listing local SSH keys: {str(e)}")


def generate_ssh_key(name, passphrase=None, key_type="rsa", key_bits=4096, ssh_dir=None):
    """
    Generate a new SSH key.
    
    Args:
        name (str): Key name
        passphrase (str, optional): Key passphrase. Defaults to None.
        key_type (str, optional): Key type (rsa, ed25519). Defaults to "rsa".
        key_bits (int, optional): Key bits (for RSA keys). Defaults to 4096.
        ssh_dir (str, optional): SSH directory. If None, uses default.
        
    Returns:
        dict: SSH key information or None if generation failed
    """
    ssh_dir = ssh_dir or DEFAULT_SSH_DIR
    
    try:
        logger.debug(f"Generating SSH key: {name} ({key_type}, {key_bits} bits)")
        
        # Create SSH directory if it doesn't exist
        os.makedirs(ssh_dir, exist_ok=True)
        
        # Validate key type
        if key_type not in ["rsa", "ed25519"]:
            logger.error(f"Invalid key type: {key_type}")
            raise ValueError(f"Invalid key type: {key_type}. Use 'rsa' or 'ed25519'.")
        
        # Validate key bits
        if key_type == "rsa" and key_bits < 2048:
            logger.warning(f"RSA key bits less than 2048 is not recommended: {key_bits}")
        
        # Generate key file paths
        key_file = os.path.join(ssh_dir, name)
        
        # Check if key already exists
        if os.path.exists(key_file) or os.path.exists(f"{key_file}.pub"):
            logger.error(f"SSH key already exists: {key_file}")
            raise FileExistsError(f"SSH key already exists: {key_file}")
        
        # Generate SSH key
        cmd = ["ssh-keygen", "-t", key_type]
        
        if key_type == "rsa":
            cmd.extend(["-b", str(key_bits)])
        
        cmd.extend(["-f", key_file, "-N", passphrase or ""])
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error generating SSH key: {result.stderr}")
            raise Exception(f"Error generating SSH key: {result.stderr}")
        
        # Get public key
        with open(f"{key_file}.pub", "r") as f:
            public_key = f.read().strip()
        
        # Get fingerprint
        fingerprint = None
        try:
            result = subprocess.run(
                ["ssh-keygen", "-lf", f"{key_file}.pub"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                fingerprint = result.stdout.strip().split()[1]
        except Exception:
            pass
        
        logger.info(f"Generated SSH key: {key_file}")
        return {
            "name": name,
            "type": key_type,
            "bits": key_bits,
            "fingerprint": fingerprint,
            "public_key": public_key,
            "private_key_file": key_file,
            "public_key_file": f"{key_file}.pub",
        }
    except Exception as e:
        logger.error(f"Error generating SSH key: {str(e)}")
        raise Exception(f"Error generating SSH key: {str(e)}")


def upload_ssh_key(title, key_path=None, key_content=None, token=None):
    """
    Upload an SSH key to GitHub.
    
    Args:
        title (str): Key title
        key_path (str, optional): Path to public key file. If None, key_content must be provided.
        key_content (str, optional): Public key content. If None, key_path must be provided.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: SSH key information or None if upload failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Uploading SSH key: {title}")
        
        # Get key content
        if key_path:
            with open(key_path, "r") as f:
                key_content = f.read().strip()
        elif not key_content:
            logger.error("Either key_path or key_content must be provided")
            raise ValueError("Either key_path or key_content must be provided")
        
        # Validate key content
        if not key_content.startswith("ssh-"):
            logger.error("Invalid SSH key format")
            raise ValueError("Invalid SSH key format. Must start with 'ssh-'.")
        
        # Upload key to GitHub
        github = Github(token)
        user = github.get_user()
        key = user.create_key(title, key_content)
        
        logger.info(f"Uploaded SSH key: {title}")
        return {
            "id": key.id,
            "title": key.title,
            "key": key.key,
            "url": key.url,
            "created_at": key.created_at,
            "verified": key.verified,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error uploading SSH key: {str(e)}")
        raise Exception(f"Error uploading SSH key: {str(e)}")


def delete_ssh_key(key_id, token=None):
    """
    Delete an SSH key from GitHub.
    
    Args:
        key_id (int): Key ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Deleting SSH key: {key_id}")
        github = Github(token)
        user = github.get_user()
        
        # Find and delete key
        for key in user.get_keys():
            if key.id == key_id:
                key.delete()
                logger.info(f"Deleted SSH key: {key_id}")
                return True
        
        logger.error(f"SSH key not found: {key_id}")
        return False
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error deleting SSH key: {str(e)}")
        raise Exception(f"Error deleting SSH key: {str(e)}")


def validate_ssh_key(key_path):
    """
    Validate an SSH key.
    
    Args:
        key_path (str): Path to key file
        
    Returns:
        dict: Validation results
    """
    try:
        logger.debug(f"Validating SSH key: {key_path}")
        
        # Check if file exists
        if not os.path.isfile(key_path):
            logger.error(f"SSH key file not found: {key_path}")
            return {
                "valid": False,
                "error": f"SSH key file not found: {key_path}",
            }
        
        # Check if file is a public key
        is_public_key = key_path.endswith(".pub")
        
        # Validate key
        if is_public_key:
            # Validate public key
            result = subprocess.run(
                ["ssh-keygen", "-lf", key_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Invalid SSH public key: {result.stderr}")
                return {
                    "valid": False,
                    "error": f"Invalid SSH public key: {result.stderr}",
                }
            
            # Parse output
            output = result.stdout.strip()
            match = re.match(r"(\d+) ([\w:]+) (.*) \((.*)\)", output)
            
            if match:
                bits, fingerprint, comment, key_type = match.groups()
                
                # Check key strength
                if key_type.startswith("RSA") and int(bits) < 2048:
                    logger.warning(f"Weak RSA key: {bits} bits")
                    return {
                        "valid": True,
                        "warning": f"Weak RSA key: {bits} bits",
                        "bits": int(bits),
                        "fingerprint": fingerprint,
                        "comment": comment,
                        "type": key_type,
                    }
                
                return {
                    "valid": True,
                    "bits": int(bits),
                    "fingerprint": fingerprint,
                    "comment": comment,
                    "type": key_type,
                }
            else:
                logger.error(f"Failed to parse SSH key information: {output}")
                return {
                    "valid": True,
                    "warning": f"Failed to parse SSH key information: {output}",
                }
        else:
            # Validate private key
            result = subprocess.run(
                ["ssh-keygen", "-yf", key_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Invalid SSH private key: {result.stderr}")
                return {
                    "valid": False,
                    "error": f"Invalid SSH private key: {result.stderr}",
                }
            
            # Get public key
            public_key = result.stdout.strip()
            
            # Write public key to temporary file
            with tempfile.NamedTemporaryFile(suffix=".pub", delete=False) as f:
                f.write(public_key.encode())
                temp_file = f.name
            
            try:
                # Validate public key
                result = subprocess.run(
                    ["ssh-keygen", "-lf", temp_file],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Invalid SSH public key: {result.stderr}")
                    return {
                        "valid": False,
                        "error": f"Invalid SSH public key: {result.stderr}",
                    }
                
                # Parse output
                output = result.stdout.strip()
                match = re.match(r"(\d+) ([\w:]+) (.*) \((.*)\)", output)
                
                if match:
                    bits, fingerprint, comment, key_type = match.groups()
                    
                    # Check key strength
                    if key_type.startswith("RSA") and int(bits) < 2048:
                        logger.warning(f"Weak RSA key: {bits} bits")
                        return {
                            "valid": True,
                            "warning": f"Weak RSA key: {bits} bits",
                            "bits": int(bits),
                            "fingerprint": fingerprint,
                            "comment": comment,
                            "type": key_type,
                        }
                    
                    return {
                        "valid": True,
                        "bits": int(bits),
                        "fingerprint": fingerprint,
                        "comment": comment,
                        "type": key_type,
                    }
                else:
                    logger.error(f"Failed to parse SSH key information: {output}")
                    return {
                        "valid": True,
                        "warning": f"Failed to parse SSH key information: {output}",
                    }
            finally:
                # Remove temporary file
                os.unlink(temp_file)
    except Exception as e:
        logger.error(f"Error validating SSH key: {str(e)}")
        return {
            "valid": False,
            "error": f"Error validating SSH key: {str(e)}",
        }
