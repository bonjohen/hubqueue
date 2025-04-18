# HubQueue Quick Start Guide

This guide will help you get started with HubQueue quickly. For more detailed information, refer to the [User Guide](user_guide.md) and [Command Reference](command_reference.md).

## Installation

1. Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/hubqueue.git
cd hubqueue
pip install -e .
```

2. Verify the installation:

```bash
hubqueue --version
```

## Authentication

1. Generate a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Click "Generate new token"
   - Select the necessary scopes (at minimum: `repo`, `user`, `gist`)
   - Copy the generated token

2. Login with your token:

```bash
hubqueue auth login
```

3. Verify your authentication:

```bash
hubqueue auth status
```

## Basic Workflow

Here's a typical workflow using HubQueue:

### 1. Create a New Repository

```bash
hubqueue repo create my-project --description "My awesome project"
```

### 2. Clone the Repository

```bash
hubqueue repo clone https://github.com/yourusername/my-project.git
cd my-project
```

### 3. Set Up Project Structure

```bash
hubqueue repo scaffold --name "My Project" --description "My awesome project"
hubqueue repo create-dirs --dirs src --dirs tests --dirs docs
```

### 4. Create a Feature Branch

```bash
hubqueue repo branch feature-branch
```

### 5. Make Changes and Commit

Make your changes to the code, then:

```bash
hubqueue repo commit "Add new feature"
```

### 6. Push Changes

```bash
hubqueue repo push
```

### 7. Create a Pull Request

```bash
hubqueue repo pr "Add new feature" --body "This PR adds a new feature"
```

## Common Commands

### Repository Management

```bash
# Create a repository
hubqueue repo create my-repo

# Clone a repository
hubqueue repo clone https://github.com/owner/repo.git

# Initialize a Git repository
hubqueue repo init --directory my-project
```

### Branch Operations

```bash
# Create a branch
hubqueue repo branch feature-branch

# Commit changes
hubqueue repo commit "Add feature"

# Push changes
hubqueue repo push
```

### Collaboration

```bash
# Create a pull request
hubqueue repo pr "Add feature"

# Fork a repository
hubqueue repo fork owner/repo

# Add a collaborator
hubqueue repo collaborator owner/repo username
```

### Issue Tracking

```bash
# List issues with filtering
hubqueue list-issues --repo owner/repo --state open --label bug

# Create a new issue
hubqueue create-issue-cmd owner/repo "Bug report" --label bug

# View issue details
hubqueue view-issue owner/repo 123

# List pull requests with filtering
hubqueue list-prs --repo owner/repo --state open --base main

# View pull request details
hubqueue view-pr owner/repo 45

# Check out a pull request locally
hubqueue checkout-pr owner/repo 45
```

### Release Management

```bash
# Update version in files
hubqueue release update-version-cmd --version 1.0.0

# Create and push a tag
hubqueue release tag v1.0.0 --push

# Generate release notes
hubqueue release notes v1.0.0 --output release-notes.md

# Create a GitHub release
hubqueue release publish owner/repo v1.0.0 --notes-file release-notes.md
```

### Workflow Automation

```bash
# List workflows
hubqueue workflow list owner/repo

# Trigger a workflow
hubqueue workflow trigger owner/repo ci.yml --input version=1.0.0

# List workflow runs
hubqueue workflow runs owner/repo --status in_progress

# View workflow run details
hubqueue workflow view owner/repo 123456789

# Manage repository secrets
hubqueue workflow secrets owner/repo
hubqueue workflow set-secret owner/repo API_KEY
```

### Gist Management

```bash
# List your gists
hubqueue gist list

# Create a new gist
hubqueue gist create --file script.py --description "My script"

# View a gist
hubqueue gist view abc123

# Update a gist
hubqueue gist update abc123 --file updated_script.py

# Download a gist
hubqueue gist download abc123 --directory gists/
```

### Project Templates

```bash
# List available templates
hubqueue template list

# Create a new template
hubqueue template create my-template ./my-project --description "My project template"

# Import a template from GitHub
hubqueue template import-github username/template-repo

# Generate a project from a template
hubqueue template generate my-template ./new-project --var project_name=awesome-app
```

### Project Management

```bash
# List project boards
hubqueue project list owner/repo

# Create a project board
hubqueue project create owner/repo "Development Roadmap"

# Create a project from a template
hubqueue project create-from-template owner/repo "Bug Triage" bug_triage

# Add an issue to a project
hubqueue project add-issue owner/repo 12345 67890 42

# Move a card between columns
hubqueue project move-card owner/repo 12345 54321 67890
```

### System Management

```bash
# Display system information
hubqueue system info

# Check dependencies
hubqueue system check-dependencies

# Check Git configuration
hubqueue system git-config

# Set up environment
hubqueue system setup

# Check for updates
hubqueue system check-updates
```

### SSH Key Management

```bash
# List SSH keys on GitHub
hubqueue ssh list

# Generate a new SSH key
hubqueue ssh generate id_github_rsa --type rsa

# Upload an SSH key to GitHub
hubqueue ssh upload ~/.ssh/id_rsa.pub

# Validate an SSH key
hubqueue ssh validate ~/.ssh/id_rsa
```

### Notifications

```bash
# List notifications
hubqueue notification list

# View notification details
hubqueue notification view 12345

# Mark a notification as read
hubqueue notification mark-read 12345

# Poll for new notifications
hubqueue notification poll
```

### Interactive Features

```bash
# Run the repository creation wizard
hubqueue wizard repository

# Run the issue creation wizard
hubqueue wizard issue --repo owner/repo

# Run the repository creation form
hubqueue form repository

# Customize the UI
hubqueue ui color --enable
hubqueue ui interactive --enable
```

### Error Handling

```bash
# Enable debug mode
hubqueue --debug repository list owner/repo

# Enable or disable debug mode
hubqueue error debug --enable

# Test error handling
hubqueue error test --type validation

# Create an error report
hubqueue error report --output error_report.json
```

## Configuration

```bash
# List all settings
hubqueue config list

# Set default editor
hubqueue config set-editor vim

# Set default repository
hubqueue config set-repo owner/repo
```

## Getting Help

```bash
# General help
hubqueue --help

# Help for a specific command group
hubqueue repo --help

# Help for a specific command
hubqueue repo create --help
```

For more detailed information, refer to the [User Guide](user_guide.md) and [Command Reference](command_reference.md).
