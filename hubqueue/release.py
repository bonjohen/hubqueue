"""
Release management module for HubQueue.
"""
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def update_version(directory=".", version=None, pattern=None, files=None):
    """
    Update version identifiers in files.
    
    Args:
        directory (str, optional): Base directory. Defaults to current directory.
        version (str, optional): New version string. If None, increments patch version.
        pattern (str, optional): Regex pattern to match version. If None, uses semantic versioning pattern.
        files (list, optional): List of files to update. If None, searches for common files.
        
    Returns:
        dict: Dictionary with old and new version, and list of updated files
    """
    # Default pattern for semantic versioning
    if not pattern:
        pattern = r'(\d+)\.(\d+)\.(\d+)'
    
    # Default files to check
    if not files:
        files = [
            "__init__.py",
            "setup.py",
            "pyproject.toml",
            "package.json",
            "VERSION",
            "version.txt",
        ]
    
    # Find files that exist
    base_dir = Path(directory)
    existing_files = []
    for file_pattern in files:
        # Handle glob patterns
        if "*" in file_pattern:
            existing_files.extend(list(base_dir.glob(file_pattern)))
        else:
            file_path = base_dir / file_pattern
            if file_path.exists():
                existing_files.append(file_path)
    
    if not existing_files:
        logger.error(f"No version files found in {directory}")
        raise FileNotFoundError(f"No version files found in {directory}")
    
    # Find current version
    current_version = None
    version_file = None
    version_match = None
    
    for file_path in existing_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(pattern, content)
            if match:
                current_version = match.group(0)
                version_file = file_path
                version_match = match
                break
    
    if not current_version:
        logger.error(f"No version matching pattern {pattern} found in files")
        raise ValueError(f"No version matching pattern {pattern} found in files")
    
    # Determine new version
    if not version:
        # Increment patch version
        if re.match(r'\d+\.\d+\.\d+', current_version):
            major, minor, patch = map(int, current_version.split('.'))
            version = f"{major}.{minor}.{patch + 1}"
        else:
            logger.error(f"Cannot auto-increment version {current_version}")
            raise ValueError(f"Cannot auto-increment version {current_version}. Please specify new version.")
    
    logger.info(f"Updating version from {current_version} to {version}")
    
    # Update files
    updated_files = []
    for file_path in existing_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = re.sub(pattern, version, content)
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated_files.append(str(file_path))
            logger.debug(f"Updated version in {file_path}")
    
    return {
        "old_version": current_version,
        "new_version": version,
        "updated_files": updated_files
    }


def create_tag(tag_name, message=None, directory=".", sign=False):
    """
    Create a Git tag for the current commit.
    
    Args:
        tag_name (str): Tag name (e.g., "v1.0.0")
        message (str, optional): Tag message. If None, uses tag name.
        directory (str, optional): Repository directory. Defaults to current directory.
        sign (bool, optional): Whether to create a signed tag. Defaults to False.
        
    Returns:
        str: Tag name if successful
    """
    if not message:
        message = f"Release {tag_name}"
    
    try:
        # Create tag
        cmd = ["git", "tag"]
        if sign:
            cmd.append("-s")
        cmd.extend(["-a", tag_name, "-m", message])
        
        logger.debug(f"Creating tag {tag_name}")
        subprocess.run(
            cmd,
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Created tag {tag_name}")
        return tag_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create tag: {e.stderr}")
        raise Exception(f"Failed to create tag: {e.stderr}")
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        raise Exception(f"Error creating tag: {str(e)}")


def push_tag(tag_name, remote="origin", directory="."):
    """
    Push a Git tag to the remote repository.
    
    Args:
        tag_name (str): Tag name to push
        remote (str, optional): Remote name. Defaults to "origin".
        directory (str, optional): Repository directory. Defaults to current directory.
        
    Returns:
        bool: True if successful
    """
    try:
        # Push tag
        logger.debug(f"Pushing tag {tag_name} to {remote}")
        subprocess.run(
            ["git", "push", remote, tag_name],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Pushed tag {tag_name} to {remote}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push tag: {e.stderr}")
        raise Exception(f"Failed to push tag: {e.stderr}")
    except Exception as e:
        logger.error(f"Error pushing tag: {str(e)}")
        raise Exception(f"Error pushing tag: {str(e)}")


def generate_release_notes(tag_name, previous_tag=None, directory="."):
    """
    Generate release notes from Git commits.
    
    Args:
        tag_name (str): Current tag name
        previous_tag (str, optional): Previous tag name. If None, uses the previous tag.
        directory (str, optional): Repository directory. Defaults to current directory.
        
    Returns:
        str: Release notes in Markdown format
    """
    try:
        # Get previous tag if not specified
        if not previous_tag:
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
                    cwd=directory,
                    check=True,
                    capture_output=True,
                    text=True
                )
                previous_tag = result.stdout.strip()
            except subprocess.CalledProcessError:
                # If no previous tag, use first commit
                result = subprocess.run(
                    ["git", "rev-list", "--max-parents=0", "HEAD"],
                    cwd=directory,
                    check=True,
                    capture_output=True,
                    text=True
                )
                previous_tag = result.stdout.strip()
        
        # Get commits between tags
        range_spec = f"{previous_tag}..HEAD" if previous_tag else "HEAD"
        result = subprocess.run(
            ["git", "log", range_spec, "--pretty=format:%h %s (%an)"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True
        )
        commits = result.stdout.strip().split("\n")
        
        # Generate release notes
        now = datetime.now().strftime("%Y-%m-%d")
        notes = f"# Release {tag_name} ({now})\n\n"
        
        if not commits or commits[0] == '':
            notes += "No changes since previous release.\n"
        else:
            # Group commits by type (feature, fix, etc.)
            features = []
            fixes = []
            docs = []
            other = []
            
            for commit in commits:
                if not commit:
                    continue
                    
                if re.search(r'feat|feature|add|new', commit, re.IGNORECASE):
                    features.append(commit)
                elif re.search(r'fix|bug|issue|error|crash', commit, re.IGNORECASE):
                    fixes.append(commit)
                elif re.search(r'doc|docs|documentation', commit, re.IGNORECASE):
                    docs.append(commit)
                else:
                    other.append(commit)
            
            if features:
                notes += "## Features\n\n"
                for commit in features:
                    notes += f"* {commit}\n"
                notes += "\n"
            
            if fixes:
                notes += "## Bug Fixes\n\n"
                for commit in fixes:
                    notes += f"* {commit}\n"
                notes += "\n"
            
            if docs:
                notes += "## Documentation\n\n"
                for commit in docs:
                    notes += f"* {commit}\n"
                notes += "\n"
            
            if other:
                notes += "## Other Changes\n\n"
                for commit in other:
                    notes += f"* {commit}\n"
                notes += "\n"
        
        logger.info(f"Generated release notes for {tag_name}")
        return notes
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate release notes: {e.stderr}")
        raise Exception(f"Failed to generate release notes: {e.stderr}")
    except Exception as e:
        logger.error(f"Error generating release notes: {str(e)}")
        raise Exception(f"Error generating release notes: {str(e)}")


def create_github_release(repo_name, tag_name, name=None, body=None, draft=False, prerelease=False, token=None):
    """
    Create a GitHub release.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        tag_name (str): Tag name for the release
        name (str, optional): Release title. If None, uses tag name.
        body (str, optional): Release description. If None, generates from commits.
        draft (bool, optional): Whether to create as draft. Defaults to False.
        prerelease (bool, optional): Whether to mark as prerelease. Defaults to False.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Release information or None if creation failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Creating GitHub release for {repo_name} with tag {tag_name}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Generate release notes if not provided
        if not body:
            try:
                body = generate_release_notes(tag_name)
            except Exception as e:
                logger.warning(f"Failed to generate release notes: {str(e)}")
                body = f"Release {tag_name}"
        
        # Create release
        release = repo.create_git_release(
            tag=tag_name,
            name=name or tag_name,
            message=body,
            draft=draft,
            prerelease=prerelease
        )
        
        logger.info(f"Created GitHub release {tag_name} for {repo_name}")
        return {
            "id": release.id,
            "tag_name": release.tag_name,
            "name": release.title,
            "body": release.body,
            "draft": release.draft,
            "prerelease": release.prerelease,
            "created_at": release.created_at,
            "html_url": release.html_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error creating GitHub release: {str(e)}")
        raise Exception(f"Error creating GitHub release: {str(e)}")


def upload_release_asset(repo_name, release_id, file_path, label=None, token=None):
    """
    Upload an asset to a GitHub release.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        release_id (int): Release ID
        file_path (str): Path to the file to upload
        label (str, optional): Label for the asset. If None, uses filename.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Asset information or None if upload failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Uploading asset {file_path} to release {release_id}")
        github = Github(token)
        repo = github.get_repo(repo_name)
        
        # Get release
        release = repo.get_release(release_id)
        
        # Upload asset
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File {file_path} does not exist")
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        asset = release.upload_asset(
            path=str(file_path),
            label=label or file_path.name,
            content_type=None  # Let GitHub determine content type
        )
        
        logger.info(f"Uploaded asset {file_path.name} to release {release_id}")
        return {
            "id": asset.id,
            "name": asset.name,
            "label": asset.label,
            "content_type": asset.content_type,
            "size": asset.size,
            "download_count": asset.download_count,
            "browser_download_url": asset.browser_download_url,
        }
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error uploading release asset: {str(e)}")
        raise Exception(f"Error uploading release asset: {str(e)}")
