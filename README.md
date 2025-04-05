# HubQueue

A command-line interface for GitHub tools that simplifies repository management, authentication, and collaboration workflows.

## Installation

Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/hubqueue.git
cd hubqueue
pip install -e .
```

## Configuration

You can configure HubQueue in two ways:

1. Set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_token
```

2. Create a configuration file:

```bash
mkdir -p ~/.hubqueue
echo '{"github_token": "your_github_token"}' > ~/.hubqueue/config.json
```

## Features

- **Authentication**: Secure GitHub authentication with token and OAuth support
- **User Preferences**: Customizable configuration for editor, default repository, and more
- **Repository Management**: Create, clone, and manage GitHub repositories
- **Branch Operations**: Create branches, commit changes, and push to remote
- **Collaboration**: Create pull requests, fork repositories, and manage collaborators
- **Issue Tracking**: List and manage repository issues and pull requests

## Usage

HubQueue provides a comprehensive set of commands organized into logical groups. Use `hubqueue --help` to see all available commands.

### Authentication

```bash
# Login with GitHub token
hubqueue auth login

# Check authentication status
hubqueue auth status

# Logout and remove stored token
hubqueue auth logout
```

### Configuration

```bash
# List all configuration settings
hubqueue config list

# Set a configuration value
hubqueue config set key value

# Set default editor
hubqueue config set-editor vim

# Set default repository
hubqueue config set-repo owner/repo
```

### Repository Management

```bash
# Create a new repository
hubqueue repo create my-new-repo --description "My awesome project"

# Clone a repository
hubqueue repo clone https://github.com/owner/repo.git

# Initialize a Git repository
hubqueue repo init --directory my-project

# Create project directories
hubqueue repo create-dirs --dirs src --dirs tests --dirs docs

# Generate standard project files
hubqueue repo scaffold --name "My Project" --description "A great project"
```

### Branch Operations

```bash
# Create and switch to a new branch
hubqueue repo branch feature-branch

# Stage and commit changes
hubqueue repo commit "Add new feature"

# Push commits to remote
hubqueue repo push
```

### Collaboration

```bash
# Create a pull request
hubqueue repo pr "Add new feature" --body "This PR adds a new feature"

# Fork a repository
hubqueue repo fork owner/repo

# Manage collaborators
hubqueue repo collaborator owner/repo username --permission push
```

### Issue Tracking

```bash
# List issues
hubqueue list-issues --repo owner/repo

# List pull requests
hubqueue list-prs --repo owner/repo
```

## Development

### Setup Development Environment

```bash
# Create and activate virtual environment
python -m venv venv_hubqueue
source venv_hubqueue/bin/activate  # On Windows: venv_hubqueue\Scripts\activate

# Install development dependencies
pip install -e .
```

### Running Tests

```bash
pytest
```

## License

[MIT](LICENSE)
