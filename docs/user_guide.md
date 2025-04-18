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
10. [Gist Management](#gist-management)
11. [Project Templates](#project-templates)
12. [Project Management](#project-management)
13. [System Management](#system-management)
14. [SSH Key Management](#ssh-key-management)
15. [Demo Script](#demo-script)
16. [Notifications](#notifications)
17. [Interactive Features](#interactive-features)
18. [Logging](#logging)

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

## Project Templates

HubQueue provides tools for managing project templates and scaffolding new projects from templates.

### Template Management

Manage project templates:

```bash
# List available templates
hubqueue template list

# View template details
hubqueue template view my-template --show-variables

# Create a new template from a directory
hubqueue template create web-app ./my-web-app --description "Web application template"

# Import a template from GitHub
hubqueue template import-github username/template-repo --name my-template

# Import a template from a URL
hubqueue template import-url https://example.com/template.zip my-template

# Delete a template
hubqueue template delete my-template
```

### Project Generation

Generate projects from templates:

```bash
# Generate a project from a template
hubqueue template generate my-template ./new-project

# Generate a project with custom variables
hubqueue template generate my-template ./new-project --var project_name=awesome-app --var author="Jane Smith"

# List template variables
hubqueue template variables my-template
```

Templates support Jinja2 templating for both file content and filenames, allowing for dynamic project generation based on provided variables.

## Project Management

HubQueue provides tools for managing GitHub Projects, including creating project boards, managing columns, and tracking issues and pull requests.

### Project Board Management

Manage GitHub Project boards:

```bash
# List project boards for a repository
hubqueue project list owner/repo

# View detailed information about a project board
hubqueue project view owner/repo 12345

# Create a new project board
hubqueue project create owner/repo "Development Roadmap" --body "Project board for tracking development tasks"

# Create a project board from a template
hubqueue project create-from-template owner/repo "Bug Triage" bug_triage

# Add a column to a project board
hubqueue project add-column owner/repo 12345 "In Review"

# Delete a project board
hubqueue project delete owner/repo 12345
```

### Project Item Management

Manage items in project boards:

```bash
# Add an issue to a project board column
hubqueue project add-issue owner/repo 12345 67890 42

# Add a pull request to a project board column
hubqueue project add-pr owner/repo 12345 67890 24

# Add a note to a project board column
hubqueue project add-note owner/repo 12345 67890 "Meeting scheduled for Friday"

# Move a card to a different column
hubqueue project move-card owner/repo 12345 54321 67890 --position top

# Delete a card from a project board
hubqueue project delete-card owner/repo 12345 54321
```

## System Management

HubQueue provides tools for managing system and environment settings, checking dependencies, and ensuring compatibility across different platforms.

### System Information

Get information about your system and environment:

```bash
# Display system information
hubqueue system info

# Export system information to a file
hubqueue system info --output system-info.json --format json

# Check dependencies
hubqueue system check-dependencies

# Install missing dependencies
hubqueue system check-dependencies --install-missing
```

### Git Configuration

Manage Git configuration:

```bash
# Check Git configuration
hubqueue system git-config

# Set Git configuration
hubqueue system git-config --set --key user.name --value "Your Name"
```

### Environment Setup

Set up and manage your environment:

```bash
# Set up environment for HubQueue
hubqueue system setup

# Export environment information
hubqueue system export --output env-info.json

# Check for updates
hubqueue system check-updates

# Install updates
hubqueue system check-updates --install
```

### Windows Compatibility

Check and set up Windows compatibility:

```bash
# Check Windows compatibility
hubqueue system windows-compatibility

# Set up Windows environment
hubqueue system windows-compatibility --setup
```

## SSH Key Management

HubQueue provides tools for managing SSH keys, including generating new keys, uploading keys to GitHub, and validating key formats.

### Managing SSH Keys

Manage your SSH keys:

```bash
# List SSH keys on GitHub
hubqueue ssh list

# List local SSH keys
hubqueue ssh list --local

# Generate a new SSH key
hubqueue ssh generate id_github_rsa --type rsa --bits 4096

# Generate and upload a new SSH key to GitHub
hubqueue ssh generate id_github_ed25519 --type ed25519 --upload

# Upload an existing SSH key to GitHub
hubqueue ssh upload ~/.ssh/id_rsa.pub --title "My Work Key"

# Validate an SSH key
hubqueue ssh validate ~/.ssh/id_rsa

# Delete an SSH key from GitHub
hubqueue ssh delete 12345
```

## Notifications

HubQueue provides tools for managing GitHub notifications, including listing, filtering, and marking notifications as read.

### Managing Notifications

Manage your GitHub notifications:

```bash
# List notifications
hubqueue notification list

# List all notifications (including read ones)
hubqueue notification list --all

# List notifications you're participating in
hubqueue notification list --participating

# View notification details
hubqueue notification view 12345

# Mark a notification as read
hubqueue notification mark-read 12345

# Mark all notifications as read
hubqueue notification mark-all-read

# Mark all notifications for a repository as read
hubqueue notification mark-all-read --repo owner/repo

# Subscribe to a notification thread
hubqueue notification subscribe 12345

# Ignore a notification thread
hubqueue notification subscribe 12345 --ignore

# Poll for new notifications
hubqueue notification poll --interval 60
```

## Interactive Features

HubQueue provides interactive features to make common tasks easier, including wizards, forms, and a rich command-line interface.

### Interactive Wizards

Wizards guide you through complex tasks step by step:

```bash
# Create a new repository with the repository wizard
hubqueue wizard repository

# Create a new issue with the issue wizard
hubqueue wizard issue --repo owner/repo

# Create a new release with the release wizard
hubqueue wizard release --repo owner/repo
```

### Interactive Forms

Forms provide a structured way to input data:

```bash
# Create a new repository with the repository form
hubqueue form repository

# Create a new issue with the issue form
hubqueue form issue --repo owner/repo
```

### UI Customization

Customize the user interface:

```bash
# Enable or disable color output
hubqueue ui color --enable
hubqueue ui color --disable

# Enable or disable interactive mode
hubqueue ui interactive --enable
hubqueue ui interactive --disable

# Clear the terminal screen
hubqueue ui clear
```

## Error Handling

HubQueue provides comprehensive error handling features to help you troubleshoot issues and recover from errors.

### Error Types

HubQueue defines several error types for different situations:

- Authentication errors: When authentication with GitHub fails
- Authorization errors: When you don't have permission to access a resource
- Not found errors: When a resource doesn't exist
- Validation errors: When input validation fails
- Rate limit errors: When you've exceeded GitHub's rate limits
- Server errors: When GitHub's servers encounter an error
- Configuration errors: When there's an issue with your configuration
- Network errors: When there's a network connectivity issue
- Input errors: When there's an issue with your input

### Error Commands

```bash
# Enable or disable debug mode
hubqueue error debug --enable
hubqueue error debug --disable

# Test error handling
hubqueue error test --type validation

# Create an error report
hubqueue error report --type network --output error_report.json

# Show detailed information about an error
hubqueue error details --type server
```

### Debug Mode

You can enable debug mode to get more detailed error messages:

```bash
# Enable debug mode for a single command
hubqueue --debug repository list owner/repo

# Enable debug mode for all commands
hubqueue error debug --enable
```

## Gist Management

HubQueue provides tools for managing GitHub Gists, including creating, updating, and interacting with gists.

### Gist Creation and Management

Create and manage GitHub Gists:

```bash
# Create a new gist from files
hubqueue gist create --file script.py --file README.md --description "My useful scripts"

# Create a gist with inline content
hubqueue gist create --content "hello.txt:Hello, world!" --description "Hello World"

# Create a public gist
hubqueue gist create --file script.py --public

# Update an existing gist
hubqueue gist update abc123 --file updated_script.py --description "Updated scripts"

# Delete a gist
hubqueue gist delete abc123
```

### Gist Listing and Viewing

List and view GitHub Gists:

```bash
# List all your gists
hubqueue gist list

# List only public gists
hubqueue gist list --public

# List starred gists
hubqueue gist list --starred

# View a gist with detailed information
hubqueue gist view abc123

# View a gist with raw file content
hubqueue gist view abc123 --raw
```

### Gist Interaction

Interact with GitHub Gists:

```bash
# Star a gist
hubqueue gist star abc123

# Unstar a gist
hubqueue gist unstar abc123

# Fork a gist
hubqueue gist fork abc123

# Add a comment to a gist
hubqueue gist comment abc123 "This is a great gist!"

# Delete a comment from a gist
hubqueue gist delete-comment abc123 12345
```

### Gist File Operations

Work with gist files locally:

```bash
# Download a gist to the local filesystem
hubqueue gist download abc123 --directory gists/

# Upload local files to a new gist
hubqueue gist upload script.py README.md --description "My project files"
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

## Demo Script

HubQueue includes a comprehensive demo script `test_hub.cmd` that demonstrates all the core functionality of the tool. This script is designed to be run outside of the project and GitHub environment, allowing you to test HubQueue in your own environment.

### Prerequisites

Before running the demo script, make sure you have:

1. Python 3.6 or higher installed
2. A GitHub account
3. A GitHub personal access token with the following scopes:
   - `repo` (Full control of private repositories)
   - `user` (Update all user data)
   - `admin:org` (Full control of orgs and teams)
   - `delete_repo` (Delete repositories)

### Running the Demo Script

**Windows:**
```cmd
test_hub.cmd
```

**Linux/macOS:**
A similar script is available in the `test_scripts` directory:
```bash
./test_scripts/test_hub_comprehensive.sh
```

### What the Demo Script Does

The demo script demonstrates the following HubQueue operations:

1. **Repository Management** - Creating, listing, updating, and deleting repositories
2. **Branch Operations** - Creating branches, setting default branches
3. **Issue Tracking** - Creating, listing, updating, and commenting on issues
4. **Release Management** - Creating, listing, and getting release details
5. **Collaboration** - Managing collaborators (example only)
6. **Notifications** - Listing notifications
7. **Interactive Features** - UI customization and error handling

### How the Demo Script Works

The script performs the following steps:

1. **Environment Setup**:
   - Checks if Python is installed
   - Creates and activates a virtual environment
   - Installs HubQueue if not already installed
   - Checks for a GitHub token and prompts for one if not found

2. **Demonstration Steps**:
   - Demonstrates repository management operations
   - Demonstrates branch operations
   - Demonstrates issue tracking operations
   - Demonstrates release management operations
   - Demonstrates collaboration features
   - Demonstrates notifications
   - Demonstrates interactive features

3. **Cleanup**:
   - Offers to delete the test repository
   - Deactivates the virtual environment

> **Note:** The script creates real repositories, issues, and other resources in your GitHub account. While it attempts to clean up after itself, make sure you understand what it's doing before running it.
