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

### Demo Script

The project includes a comprehensive demo script `test_hub.cmd` that demonstrates all the core functionality of HubQueue. This script is designed to be run outside of the project and GitHub environment, allowing you to test HubQueue in your own environment.

#### Prerequisites

Before running the demo script, make sure you have:

1. Python 3.6 or higher installed
2. A GitHub account
3. A GitHub personal access token with the following scopes:
   - `repo` (Full control of private repositories)
   - `user` (Update all user data)
   - `admin:org` (Full control of orgs and teams)
   - `delete_repo` (Delete repositories)

#### Running the Demo Script

**Windows:**
```cmd
test_hub.cmd
```

**Linux/macOS:**
A similar script is available in the `test_scripts` directory:
```bash
./test_scripts/test_hub_comprehensive.sh
```

#### What the Demo Script Does

The demo script demonstrates the following HubQueue operations:

1. **Repository Management** - Creating, listing, updating, and deleting repositories
2. **Branch Operations** - Creating branches, setting default branches
3. **Issue Tracking** - Creating, listing, updating, and commenting on issues
4. **Release Management** - Creating, listing, and getting release details
5. **Collaboration** - Managing collaborators (example only)
6. **Notifications** - Listing notifications
7. **Interactive Features** - UI customization and error handling

> **Note:** The script creates real repositories, issues, and other resources in your GitHub account. While it attempts to clean up after itself, make sure you understand what it's doing before running it.

### Project Setup Scripts

HubQueue also includes scripts for setting up basic Python and JavaScript projects:

#### Python Project Setup

```cmd
proj_setup_python.cmd project_name
```

This script creates a basic Python project with:
- Project structure with source, tests, and docs directories
- Virtual environment for Python version management
- setup.py, requirements.txt, and other configuration files
- Sample module and test

#### JavaScript Project Setup

```cmd
proj_setup_js.cmd project_name
```

This script creates a basic JavaScript project with:
- Project structure with source, test, and docs directories
- package.json for Node.js package management
- ESLint, Prettier, and Jest configuration
- Sample module and test

See [PROJECT_SETUP_README.md](PROJECT_SETUP_README.md) for more details.

## License

[MIT](LICENSE)
