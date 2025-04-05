"""
Repository management module for HubQueue.
"""
import os
import subprocess
import shutil
from pathlib import Path
import tempfile
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .utils import get_config_dir


def create_repository(name, description=None, private=False, token=None):
    """
    Create a new repository on GitHub.
    
    Args:
        name (str): Repository name
        description (str, optional): Repository description
        private (bool, optional): Whether the repository is private
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Repository information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        return None
        
    try:
        github = Github(token)
        user = github.get_user()
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=True
        )
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": repo.private,
            "html_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        raise Exception(f"Failed to create repository: {error_message}")
    except Exception as e:
        raise Exception(f"Error creating repository: {str(e)}")


def clone_repository(repo_url, directory=None, token=None):
    """
    Clone a repository to the local machine.
    
    Args:
        repo_url (str): Repository URL (HTTPS or SSH)
        directory (str, optional): Directory to clone into. If None, uses repo name.
        token (str, optional): GitHub token for private repos. If None, will try to get from config.
        
    Returns:
        str: Path to the cloned repository or None if cloning failed
    """
    # If token is provided and repo_url is HTTPS, add token to URL
    if token and repo_url.startswith("https://"):
        # Extract the domain and path
        parts = repo_url.split("//")
        if len(parts) > 1:
            domain_path = parts[1]
            repo_url = f"https://{token}@{domain_path}"
    
    # Determine target directory
    if not directory:
        # Extract repo name from URL
        repo_name = repo_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        directory = repo_name
    
    # Create directory if it doesn't exist
    directory_path = Path(directory)
    if directory_path.exists() and any(directory_path.iterdir()):
        raise Exception(f"Directory '{directory}' already exists and is not empty")
    
    try:
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, directory],
            check=True,
            capture_output=True,
            text=True
        )
        return str(directory_path.absolute())
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error cloning repository: {str(e)}")


def init_repository(directory="."):
    """
    Initialize a Git repository in the specified directory.
    
    Args:
        directory (str, optional): Directory to initialize. Defaults to current directory.
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    directory_path = Path(directory)
    
    # Create directory if it doesn't exist
    if not directory_path.exists():
        directory_path.mkdir(parents=True)
    
    # Check if .git directory already exists
    git_dir = directory_path / ".git"
    if git_dir.exists():
        raise Exception(f"Git repository already exists in '{directory}'")
    
    try:
        # Initialize the repository
        result = subprocess.run(
            ["git", "init"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Set initial branch name to main
        result = subprocess.run(
            ["git", "checkout", "-b", "main"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to initialize repository: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error initializing repository: {str(e)}")


def create_project_directories(directory=".", dirs=None):
    """
    Create essential project directories.
    
    Args:
        directory (str, optional): Base directory. Defaults to current directory.
        dirs (list, optional): List of directories to create. If None, uses default dirs.
        
    Returns:
        list: List of created directories
    """
    if dirs is None:
        dirs = ["src", "tests", "docs"]
    
    base_dir = Path(directory)
    created_dirs = []
    
    for dir_name in dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            created_dirs.append(str(dir_path))
    
    return created_dirs


def generate_gitignore(directory=".", template="Python"):
    """
    Generate a .gitignore file based on a template.
    
    Args:
        directory (str, optional): Directory to create .gitignore in. Defaults to current directory.
        template (str, optional): Template name. Defaults to "Python".
        
    Returns:
        str: Path to the created .gitignore file or None if creation failed
    """
    gitignore_path = Path(directory) / ".gitignore"
    
    # Check if .gitignore already exists
    if gitignore_path.exists():
        raise Exception(f".gitignore already exists in '{directory}'")
    
    try:
        # Fetch gitignore template from GitHub
        url = f"https://raw.githubusercontent.com/github/gitignore/main/{template}.gitignore"
        result = subprocess.run(
            ["curl", "-s", url],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Write to .gitignore file
        with open(gitignore_path, "w") as f:
            f.write(result.stdout)
        
        return str(gitignore_path)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to fetch gitignore template: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error creating .gitignore: {str(e)}")


def generate_readme(directory=".", project_name=None, description=None):
    """
    Generate a README.md file.
    
    Args:
        directory (str, optional): Directory to create README.md in. Defaults to current directory.
        project_name (str, optional): Project name. If None, uses directory name.
        description (str, optional): Project description.
        
    Returns:
        str: Path to the created README.md file or None if creation failed
    """
    readme_path = Path(directory) / "README.md"
    
    # Check if README.md already exists
    if readme_path.exists():
        raise Exception(f"README.md already exists in '{directory}'")
    
    # Determine project name if not provided
    if not project_name:
        project_name = Path(directory).absolute().name
    
    # Create README content
    content = f"# {project_name}\n\n"
    if description:
        content += f"{description}\n\n"
    content += "## Installation\n\n```bash\n# Clone the repository\ngit clone <repository-url>\ncd {project_name}\n\n# Install dependencies\npip install -r requirements.txt\n```\n\n"
    content += "## Usage\n\n```bash\n# Add usage examples here\n```\n\n"
    content += "## License\n\nThis project is licensed under the MIT License - see the LICENSE file for details.\n"
    
    try:
        # Write to README.md file
        with open(readme_path, "w") as f:
            f.write(content)
        
        return str(readme_path)
    except Exception as e:
        raise Exception(f"Error creating README.md: {str(e)}")


def generate_license(directory=".", license_type="MIT", author=None):
    """
    Generate a LICENSE file.
    
    Args:
        directory (str, optional): Directory to create LICENSE in. Defaults to current directory.
        license_type (str, optional): License type. Defaults to "MIT".
        author (str, optional): Author name. If None, tries to get from git config.
        
    Returns:
        str: Path to the created LICENSE file or None if creation failed
    """
    license_path = Path(directory) / "LICENSE"
    
    # Check if LICENSE already exists
    if license_path.exists():
        raise Exception(f"LICENSE already exists in '{directory}'")
    
    # Get current year
    import datetime
    year = datetime.datetime.now().year
    
    # Get author name if not provided
    if not author:
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                check=True,
                capture_output=True,
                text=True
            )
            author = result.stdout.strip()
        except:
            author = "Your Name"
    
    # Create license content based on type
    if license_type.upper() == "MIT":
        content = f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    else:
        raise Exception(f"Unsupported license type: {license_type}")
    
    try:
        # Write to LICENSE file
        with open(license_path, "w") as f:
            f.write(content)
        
        return str(license_path)
    except Exception as e:
        raise Exception(f"Error creating LICENSE: {str(e)}")


def create_branch(branch_name, base_branch="main", directory="."):
    """
    Create and switch to a new feature branch.
    
    Args:
        branch_name (str): Name of the new branch
        base_branch (str, optional): Base branch to create from. Defaults to "main".
        directory (str, optional): Repository directory. Defaults to current directory.
        
    Returns:
        str: Name of the created branch or None if creation failed
    """
    try:
        # Make sure we're on the base branch
        subprocess.run(
            ["git", "checkout", base_branch],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Pull latest changes
        subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Create and switch to new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        return branch_name
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to create branch: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error creating branch: {str(e)}")


def stage_and_commit(message, directory=".", files=None):
    """
    Stage and commit changes to the repository.
    
    Args:
        message (str): Commit message
        directory (str, optional): Repository directory. Defaults to current directory.
        files (list, optional): List of files to stage. If None, stages all changes.
        
    Returns:
        str: Commit hash or None if commit failed
    """
    try:
        # Stage files
        if files:
            for file in files:
                subprocess.run(
                    ["git", "add", file],
                    cwd=directory,
                    check=True,
                    capture_output=True,
                    text=True
                )
        else:
            subprocess.run(
                ["git", "add", "."],
                cwd=directory,
                check=True,
                capture_output=True,
                text=True
            )
        
        # Commit changes
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Get commit hash
        commit_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        return commit_hash
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to commit changes: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error committing changes: {str(e)}")


def push_commits(remote="origin", branch=None, directory="."):
    """
    Push commits to the remote repository.
    
    Args:
        remote (str, optional): Remote name. Defaults to "origin".
        branch (str, optional): Branch to push. If None, pushes current branch.
        directory (str, optional): Repository directory. Defaults to current directory.
        
    Returns:
        bool: True if push was successful, False otherwise
    """
    try:
        # Get current branch if not specified
        if not branch:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=directory,
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
        
        # Push to remote
        subprocess.run(
            ["git", "push", "-u", remote, branch],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to push commits: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error pushing commits: {str(e)}")


def create_pull_request(title, body=None, base_branch="main", head_branch=None, repo=None, token=None):
    """
    Create a pull request from the current branch to the main branch.
    
    Args:
        title (str): Pull request title
        body (str, optional): Pull request description
        base_branch (str, optional): Base branch for PR. Defaults to "main".
        head_branch (str, optional): Head branch for PR. If None, uses current branch.
        repo (str, optional): Repository name in format 'owner/repo'. If None, tries to determine from remote.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Pull request information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        return None
    
    try:
        # Get current directory
        directory = "."
        
        # Get current branch if not specified
        if not head_branch:
            head_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=directory,
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
        
        # Get repo from remote if not specified
        if not repo:
            remote_url = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=directory,
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Extract owner/repo from URL
            if "github.com" in remote_url:
                if remote_url.startswith("git@"):
                    # SSH URL format: git@github.com:owner/repo.git
                    repo = remote_url.split(":")[-1].replace(".git", "")
                else:
                    # HTTPS URL format: https://github.com/owner/repo.git
                    repo = remote_url.split("github.com/")[-1].replace(".git", "")
        
        if not repo:
            raise Exception("Could not determine repository name")
        
        # Create pull request
        github = Github(token)
        github_repo = github.get_repo(repo)
        pr = github_repo.create_pull(
            title=title,
            body=body,
            base=base_branch,
            head=head_branch
        )
        
        return {
            "number": pr.number,
            "title": pr.title,
            "html_url": pr.html_url,
            "state": pr.state,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        raise Exception(f"Failed to create pull request: {error_message}")
    except Exception as e:
        raise Exception(f"Error creating pull request: {str(e)}")


def fork_repository(repo_name, token=None):
    """
    Fork an existing repository to the user's GitHub account.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Forked repository information or None if fork failed
    """
    token = token or get_github_token()
    if not token:
        return None
    
    try:
        github = Github(token)
        repo = github.get_repo(repo_name)
        fork = repo.create_fork()
        
        return {
            "name": fork.name,
            "full_name": fork.full_name,
            "description": fork.description,
            "html_url": fork.html_url,
            "clone_url": fork.clone_url,
            "ssh_url": fork.ssh_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        raise Exception(f"Failed to fork repository: {error_message}")
    except Exception as e:
        raise Exception(f"Error forking repository: {str(e)}")


def manage_collaborators(repo_name, username, permission="push", add=True, token=None):
    """
    Manage repository collaborators and permissions.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        username (str): GitHub username to add/remove
        permission (str, optional): Permission level (pull, push, admin). Defaults to "push".
        add (bool, optional): Whether to add (True) or remove (False) the collaborator. Defaults to True.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if operation was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        return False
    
    try:
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        if add:
            # Add collaborator
            repo.add_to_collaborators(username, permission)
        else:
            # Remove collaborator
            repo.remove_from_collaborators(username)
        
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        raise Exception(f"Failed to manage collaborator: {error_message}")
    except Exception as e:
        raise Exception(f"Error managing collaborator: {str(e)}")
