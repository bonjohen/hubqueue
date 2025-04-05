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

List open issues for a repository:

```bash
hubqueue list-issues --repo owner/repo
```

### Listing Pull Requests

List open pull requests for a repository:

```bash
hubqueue list-prs --repo owner/repo
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

## Environment Variables

HubQueue respects the following environment variables:

- `GITHUB_TOKEN`: GitHub API token
- `HUBQUEUE_EDITOR`: Preferred text editor
- `EDITOR`: Fallback text editor
- `VISUAL`: Another fallback text editor

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
