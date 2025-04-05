# HubQueue User Guide

This guide provides detailed information on how to use HubQueue, a command-line interface for GitHub tools that simplifies repository management, authentication, and collaboration workflows.

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Configuration](#configuration)
4. [Repository Management](#repository-management)
5. [Branch Operations](#branch-operations)
6. [Collaboration](#collaboration)
7. [Issue Tracking](#issue-tracking)
8. [Release Management](#release-management)
9. [Workflow Automation](#workflow-automation)
10. [Logging](#logging)

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account

### Installing HubQueue

Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/hubqueue.git
cd hubqueue
pip install -e .
```

## Authentication

HubQueue requires authentication with GitHub to access repositories and perform operations. There are two ways to authenticate:

### Token-based Authentication

1. **Generate a GitHub Personal Access Token**:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Click "Generate new token"
   - Select the necessary scopes (at minimum: `repo`, `user`, `gist`)
   - Copy the generated token

2. **Login with the Token**:
   ```bash
   hubqueue auth login
   ```
   You will be prompted to enter your token.

3. **Check Authentication Status**:
   ```bash
   hubqueue auth status
   ```
   This will display your GitHub username and account information if you're logged in.

4. **Logout**:
   ```bash
   hubqueue auth logout
   ```
   This will remove the stored token.

### OAuth Authentication

For a more secure authentication flow:

```bash
hubqueue auth oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

This will open a browser window for GitHub authorization and prompt you to enter the authorization code.

## Configuration

HubQueue allows you to customize various settings to improve your workflow.

### Managing Configuration

1. **List All Settings**:
   ```bash
   hubqueue config list
   ```

2. **Get a Specific Setting**:
   ```bash
   hubqueue config get editor
   ```

3. **Set a Configuration Value**:
   ```bash
   hubqueue config set key value
   ```

### Common Configuration Options

1. **Default Editor**:
   ```bash
   hubqueue config set-editor vim
   ```
   Sets your preferred text editor for editing files.

2. **Default Repository**:
   ```bash
   hubqueue config set-repo owner/repo
   ```
   Sets a default repository for commands that require a repository.

3. **Get Current Editor**:
   ```bash
   hubqueue config get-editor-cmd
   ```

4. **Get Default Repository**:
   ```bash
   hubqueue config get-repo
   ```

## Repository Management

HubQueue provides comprehensive tools for managing GitHub repositories.

### Creating Repositories

Create a new repository on GitHub:

```bash
hubqueue repo create my-new-repo --description "My awesome project" --private
```

Options:
- `--description`: Repository description
- `--private/--public`: Repository visibility (default: public)

### Cloning Repositories

Clone a repository to your local machine:

```bash
hubqueue repo clone https://github.com/owner/repo.git --directory my-local-dir
```

Options:
- `--directory`: Directory to clone into (default: repository name)
- `--token`: GitHub token for private repositories

### Initializing Git Repositories

Initialize a Git repository in a directory:

```bash
hubqueue repo init --directory my-project
```

This initializes a Git repository with a main branch.

### Creating Project Directories

Create standard project directories:

```bash
hubqueue repo create-dirs --dirs src --dirs tests --dirs docs
```

You can specify multiple directories with the `--dirs` option.

### Generating Project Files

Generate standard project files (README.md, .gitignore, LICENSE):

```bash
hubqueue repo scaffold --name "My Project" --description "A great project" --license MIT --author "Your Name" --gitignore Python
```

Options:
- `--name`: Project name
- `--description`: Project description
- `--license`: License type (default: MIT)
- `--author`: Author name for license
- `--gitignore`: Gitignore template (default: Python)

## Branch Operations

Manage Git branches and commits with HubQueue.

### Creating Branches

Create and switch to a new feature branch:

```bash
hubqueue repo branch feature-branch --base main
```

Options:
- `--base`: Base branch to create from (default: main)
- `--directory`: Repository directory (default: current directory)

### Committing Changes

Stage and commit changes to the repository:

```bash
hubqueue repo commit "Add new feature" --files file1.py --files file2.py
```

Options:
- `--files`: Specific files to stage (default: all changes)
- `--directory`: Repository directory (default: current directory)

### Pushing Commits

Push commits to the remote repository:

```bash
hubqueue repo push --remote origin --branch feature-branch
```

Options:
- `--remote`: Remote name (default: origin)
- `--branch`: Branch to push (default: current branch)
- `--directory`: Repository directory (default: current directory)

## Collaboration

HubQueue simplifies collaboration on GitHub projects.

### Creating Pull Requests

Create a pull request from your current branch:

```bash
hubqueue repo pr "Add new feature" --body "This PR adds a new feature" --base main
```

Options:
- `--body`: Pull request description
- `--base`: Base branch for PR (default: main)
- `--head`: Head branch for PR (default: current branch)
- `--repo`: Repository name in format 'owner/repo' (default: determined from remote)

### Forking Repositories

Fork an existing repository to your GitHub account:

```bash
hubqueue repo fork owner/repo
```

### Managing Collaborators

Add or remove collaborators from your repository:

```bash
# Add a collaborator
hubqueue repo collaborator owner/repo username --permission push

# Remove a collaborator
hubqueue repo collaborator owner/repo username --remove
```

Options:
- `--permission`: Permission level (pull, push, admin) (default: push)
- `--remove`: Remove collaborator instead of adding

## Issue Tracking

Track and manage issues and pull requests.

### Listing Issues

List issues for a repository with various filtering options:

```bash
# List all open issues
hubqueue list-issues --repo owner/repo

# List closed issues
hubqueue list-issues --repo owner/repo --state closed

# List issues with specific labels
hubqueue list-issues --repo owner/repo --label bug --label enhancement

# List issues assigned to a specific user
hubqueue list-issues --repo owner/repo --assignee username

# Display issues in a table format
hubqueue list-issues --repo owner/repo --format table
```

### Creating Issues

Create a new issue in a repository:

```bash
# Create a simple issue
hubqueue create-issue-cmd owner/repo "Issue title"

# Create an issue with a body
hubqueue create-issue-cmd owner/repo "Issue title" --body "Detailed description of the issue"

# Create an issue with labels and assignees
hubqueue create-issue-cmd owner/repo "Issue title" --label bug --label priority --assignee username
```

### Viewing Issue Details

View detailed information about a specific issue:

```bash
hubqueue view-issue owner/repo 123
```

This will display the issue title, description, status, labels, assignees, and all comments.

### Listing Pull Requests

List pull requests for a repository with various filtering options:

```bash
# List all open pull requests
hubqueue list-prs --repo owner/repo

# List closed pull requests
hubqueue list-prs --repo owner/repo --state closed

# List pull requests targeting a specific branch
hubqueue list-prs --repo owner/repo --base main

# List pull requests from a specific branch
hubqueue list-prs --repo owner/repo --head feature-branch

# Display pull requests in a table format
hubqueue list-prs --repo owner/repo --format table
```

### Viewing Pull Request Details

View detailed information about a specific pull request:

```bash
hubqueue view-pr owner/repo 123
```

This will display the pull request title, description, status, branches, changes, commits, and all comments.

### Checking Out Pull Requests

Check out a pull request locally for review:

```bash
# Check out a pull request in the current directory
hubqueue checkout-pr owner/repo 123

# Check out a pull request in a specific directory
hubqueue checkout-pr owner/repo 123 --directory path/to/repo
```

This will fetch the pull request and create a local branch named `pr-123` that you can review and test.

## Release Management

HubQueue provides tools for managing releases, including version updates, tagging, and GitHub releases.

### Version Management

Update version identifiers in your project files:

```bash
# Auto-increment patch version (e.g., 1.0.0 -> 1.0.1)
hubqueue release update-version-cmd

# Set specific version
hubqueue release update-version-cmd --version 2.0.0

# Use custom version pattern
hubqueue release update-version-cmd --pattern "v\d+\.\d+"

# Update specific files
hubqueue release update-version-cmd --file setup.py --file __init__.py
```

### Git Tagging

Create and manage Git tags for releases:

```bash
# Create a tag
hubqueue release tag v1.0.0 --message "Release version 1.0.0"

# Create a signed tag
hubqueue release tag v1.0.0 --sign

# Create and push a tag
hubqueue release tag v1.0.0 --push
```

### Release Notes

Generate release notes from Git commits:

```bash
# Generate release notes between the previous tag and HEAD
hubqueue release notes v1.0.0

# Generate release notes between specific tags
hubqueue release notes v1.0.0 --previous-tag v0.9.0

# Save release notes to a file
hubqueue release notes v1.0.0 --output release-notes.md
```

The generated release notes will categorize commits into features, bug fixes, documentation, and other changes based on commit message patterns.

### GitHub Releases

Create GitHub releases and upload assets:

```bash
# Create a simple release
hubqueue release publish owner/repo v1.0.0

# Create a release with a custom title
hubqueue release publish owner/repo v1.0.0 --name "Version 1.0.0"

# Create a release with release notes from a file
hubqueue release publish owner/repo v1.0.0 --notes-file release-notes.md

# Create a draft release
hubqueue release publish owner/repo v1.0.0 --draft

# Create a prerelease
hubqueue release publish owner/repo v1.0.0 --prerelease

# Upload assets to the release
hubqueue release publish owner/repo v1.0.0 --asset dist/app.zip --asset docs/manual.pdf
```

## Workflow Automation

HubQueue provides tools for managing GitHub Actions workflows, including triggering, monitoring, and managing workflow runs.

### Workflow Management

List and trigger GitHub Actions workflows:

```bash
# List all workflows in a repository
hubqueue workflow list owner/repo

# Trigger a workflow by ID or filename
hubqueue workflow trigger owner/repo ci.yml --ref main

# Trigger a workflow with input parameters
hubqueue workflow trigger owner/repo ci.yml --input version=1.0.0 --input environment=production

# Trigger and monitor a workflow until completion
hubqueue workflow trigger owner/repo ci.yml --monitor --timeout 600
```

### Workflow Run Management

List, view, and manage workflow runs:

```bash
# List workflow runs
hubqueue workflow runs owner/repo

# Filter runs by status, branch, or workflow
hubqueue workflow runs owner/repo --status completed --branch main --workflow ci.yml

# View detailed information about a workflow run
hubqueue workflow view owner/repo 123456789

# Cancel a workflow run
hubqueue workflow cancel owner/repo 123456789

# Rerun a workflow run
hubqueue workflow rerun owner/repo 123456789
```

### Repository Secrets

Manage GitHub repository secrets:

```bash
# List repository secrets
hubqueue workflow secrets owner/repo

# Create or update a secret
hubqueue workflow set-secret owner/repo API_KEY

# Delete a secret
hubqueue workflow delete-secret owner/repo API_KEY
```

### Workflow Caches

Manage GitHub Actions caches:

```bash
# List workflow caches
hubqueue workflow caches owner/repo

# Delete a cache by ID
hubqueue workflow delete-cache owner/repo --id 12345

# Delete a cache by key
hubqueue workflow delete-cache owner/repo --key npm-cache
```

## Command Reference

For a complete list of commands and options, use the help flag:

```bash
# General help
hubqueue --help

# Help for a specific command group
hubqueue repo --help

# Help for a specific command
hubqueue repo create --help
```

## Logging

HubQueue includes a comprehensive logging system that can help you debug issues and track operations.

### Log Levels

You can set the log level when running HubQueue commands:

```bash
hubqueue --log-level debug list-issues --repo owner/repo
```

Available log levels (from most to least verbose):
- `debug`: Detailed debugging information
- `info`: General information about operations (default)
- `warning`: Warning messages
- `error`: Error messages
- `critical`: Critical errors

### Log File

You can also log to a file:

```bash
hubqueue --log-file hubqueue.log list-issues --repo owner/repo
```

This will write logs to the specified file in addition to displaying them in the console.

## Environment Variables

HubQueue respects the following environment variables:

- `GITHUB_TOKEN`: GitHub API token
- `HUBQUEUE_EDITOR`: Preferred text editor
- `EDITOR`: Fallback text editor
- `VISUAL`: Another fallback text editor
- `HUBQUEUE_LOG_LEVEL`: Default log level
- `HUBQUEUE_LOG_FILE`: Default log file path

## Configuration File

HubQueue stores configuration in `~/.hubqueue/config.json`. You can edit this file directly, but it's recommended to use the `config` commands instead.

Example configuration file:

```json
{
  "github_token": "your_github_token",
  "preferences": {
    "editor": "vim",
    "default_repo": "owner/repo"
  }
}
```
