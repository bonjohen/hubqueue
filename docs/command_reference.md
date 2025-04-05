# HubQueue Command Reference

This document provides a comprehensive reference for all commands available in HubQueue.

## Global Options

These options are available for all HubQueue commands:

- `--help`: Show help message and exit
- `--version`: Show version and exit

## Main Commands

### `hubqueue`

The main entry point for HubQueue.

```
hubqueue [OPTIONS] COMMAND [ARGS]...
```

Options:
- `--version`: Show the version and exit.
- `--help`: Show help message and exit.
- `--log-level`: Set the logging level (debug, info, warning, error, critical). Default: info.
- `--log-file`: Log to this file in addition to the console.

## Authentication Commands

### `hubqueue auth`

Authentication commands for GitHub.

```
hubqueue auth [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue auth login`

Login with GitHub token.

```
hubqueue auth login [OPTIONS]
```

Options:
- `--token`: GitHub API token (will prompt if not provided)

#### `hubqueue auth logout`

Logout and remove stored GitHub token.

```
hubqueue auth logout [OPTIONS]
```

#### `hubqueue auth status`

Check authentication status.

```
hubqueue auth status [OPTIONS]
```

#### `hubqueue auth oauth`

Login with GitHub OAuth.

```
hubqueue auth oauth [OPTIONS]
```

Options:
- `--client-id`: GitHub OAuth client ID (required)
- `--client-secret`: GitHub OAuth client secret (required)

## Configuration Commands

### `hubqueue config`

Configuration commands for HubQueue.

```
hubqueue config [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue config list`

List all configuration settings.

```
hubqueue config list [OPTIONS]
```

#### `hubqueue config get`

Get a configuration setting.

```
hubqueue config get [OPTIONS] KEY
```

Arguments:
- `KEY`: The configuration key to get

#### `hubqueue config set`

Set a configuration setting.

```
hubqueue config set [OPTIONS] KEY VALUE
```

Arguments:
- `KEY`: The configuration key to set
- `VALUE`: The value to set

#### `hubqueue config set-editor`

Set the default text editor.

```
hubqueue config set-editor [OPTIONS] EDITOR
```

Arguments:
- `EDITOR`: The text editor command

#### `hubqueue config get-editor-cmd`

Get the default text editor.

```
hubqueue config get-editor-cmd [OPTIONS]
```

#### `hubqueue config set-repo`

Set the default repository (format: owner/repo).

```
hubqueue config set-repo [OPTIONS] REPO
```

Arguments:
- `REPO`: Repository in format 'owner/repo'

#### `hubqueue config get-repo`

Get the default repository.

```
hubqueue config get-repo [OPTIONS]
```

## Repository Management Commands

### `hubqueue repo`

Repository management commands.

```
hubqueue repo [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue repo create`

Create a new repository on GitHub.

```
hubqueue repo create [OPTIONS] NAME
```

Arguments:
- `NAME`: Repository name

Options:
- `--description`: Repository description
- `--private/--public`: Whether the repository is private (default: public)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue repo clone`

Clone a repository to the local machine.

```
hubqueue repo clone [OPTIONS] URL
```

Arguments:
- `URL`: Repository URL (HTTPS or SSH)

Options:
- `--directory`: Directory to clone into
- `--token`: GitHub API token for private repos (or set GITHUB_TOKEN env variable)

#### `hubqueue repo init`

Initialize a Git repository in a specified directory.

```
hubqueue repo init [OPTIONS]
```

Options:
- `--directory`: Directory to initialize (default: current directory)

#### `hubqueue repo create-dirs`

Create essential project directories.

```
hubqueue repo create-dirs [OPTIONS]
```

Options:
- `--directory`: Base directory (default: current directory)
- `--dirs`: Directories to create (can be specified multiple times)

#### `hubqueue repo scaffold`

Generate standard project files (README.md, .gitignore, LICENSE).

```
hubqueue repo scaffold [OPTIONS]
```

Options:
- `--directory`: Directory to create files in (default: current directory)
- `--name`: Project name (defaults to directory name)
- `--description`: Project description
- `--license`: License type (default: MIT)
- `--author`: Author name for license
- `--gitignore`: Gitignore template (default: Python)

#### `hubqueue repo branch`

Create and switch to a new feature branch.

```
hubqueue repo branch [OPTIONS] BRANCH_NAME
```

Arguments:
- `BRANCH_NAME`: Name of the branch to create

Options:
- `--base`: Base branch to create from (default: main)
- `--directory`: Repository directory (default: current directory)

#### `hubqueue repo commit`

Stage and commit changes to the repository.

```
hubqueue repo commit [OPTIONS] MESSAGE
```

Arguments:
- `MESSAGE`: Commit message

Options:
- `--directory`: Repository directory (default: current directory)
- `--files`: Files to stage (can be specified multiple times)

#### `hubqueue repo push`

Push commits to the remote repository.

```
hubqueue repo push [OPTIONS]
```

Options:
- `--remote`: Remote name (default: origin)
- `--branch`: Branch to push (default: current branch)
- `--directory`: Repository directory (default: current directory)

#### `hubqueue repo pr`

Create a pull request from the current branch to the main branch.

```
hubqueue repo pr [OPTIONS] TITLE
```

Arguments:
- `TITLE`: Pull request title

Options:
- `--body`: Pull request description
- `--base`: Base branch for PR (default: main)
- `--head`: Head branch for PR (default: current branch)
- `--repo`: Repository name in format 'owner/repo'
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue repo fork`

Fork an existing repository to your GitHub account.

```
hubqueue repo fork [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue repo collaborator`

Manage repository collaborators and permissions.

```
hubqueue repo collaborator [OPTIONS] REPO_NAME USERNAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `USERNAME`: GitHub username to add/remove

Options:
- `--permission`: Permission level (pull, push, admin) (default: push)
- `--remove`: Remove collaborator instead of adding
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

## Issue and Pull Request Commands

### `hubqueue create-issue-cmd`

Create a new issue in a repository.

```
hubqueue create-issue-cmd [OPTIONS] REPO_NAME TITLE
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `TITLE`: Issue title

Options:
- `--body`: Issue body
- `--label`: Label to apply (can be specified multiple times)
- `--assignee`: Username to assign (can be specified multiple times)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

### `hubqueue view-issue`

View detailed information about an issue.

```
hubqueue view-issue [OPTIONS] REPO_NAME ISSUE_NUMBER
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `ISSUE_NUMBER`: Issue number

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

### `hubqueue view-pr`

View detailed information about a pull request.

```
hubqueue view-pr [OPTIONS] REPO_NAME PR_NUMBER
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PR_NUMBER`: Pull request number

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

### `hubqueue checkout-pr`

Checkout a pull request locally for review.

```
hubqueue checkout-pr [OPTIONS] REPO_NAME PR_NUMBER
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PR_NUMBER`: Pull request number

Options:
- `--directory`: Repository directory (default: current directory)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

### `hubqueue list-issues`

List issues for a repository.

```
hubqueue list-issues [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'
- `--state`: Issue state (open, closed, all) (default: open)
- `--label`: Filter by label (can be specified multiple times)
- `--assignee`: Filter by assignee username
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--format`: Output format (table, simple) (default: simple)

### `hubqueue list-prs`

List pull requests for a repository.

```
hubqueue list-prs [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'
- `--state`: Pull request state (open, closed, all) (default: open)
- `--base`: Filter by base branch name
- `--head`: Filter by head branch name
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--format`: Output format (table, simple) (default: simple)

## Release Management Commands

### `hubqueue release`

Release management commands.

```
hubqueue release [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue release update-version-cmd`

Update version identifiers in files.

```
hubqueue release update-version-cmd [OPTIONS]
```

Options:
- `--directory`: Base directory (default: current directory)
- `--version`: New version string (default: increment patch version)
- `--pattern`: Regex pattern to match version (default: semantic versioning)
- `--file`: File to update (can be specified multiple times)

#### `hubqueue release tag`

Create a Git tag for the current commit.

```
hubqueue release tag [OPTIONS] TAG_NAME
```

Arguments:
- `TAG_NAME`: Tag name (e.g., "v1.0.0")

Options:
- `--message`: Tag message (default: 'Release TAG_NAME')
- `--directory`: Repository directory (default: current directory)
- `--sign`: Create a signed tag
- `--push`: Push tag to remote after creation
- `--remote`: Remote name for pushing (default: origin)

#### `hubqueue release notes`

Generate release notes from Git commits.

```
hubqueue release notes [OPTIONS] TAG_NAME
```

Arguments:
- `TAG_NAME`: Tag name for the release

Options:
- `--previous-tag`: Previous tag name for comparison
- `--directory`: Repository directory (default: current directory)
- `--output`: Output file for release notes (default: print to console)

#### `hubqueue release publish`

Create a GitHub release and optionally upload assets.

```
hubqueue release publish [OPTIONS] REPO_NAME TAG_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `TAG_NAME`: Tag name for the release

Options:
- `--name`: Release title (default: tag name)
- `--notes-file`: File containing release notes
- `--draft`: Create as draft release
- `--prerelease`: Mark as prerelease
- `--asset`: Asset file to upload (can be specified multiple times)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

## Workflow Automation Commands

### `hubqueue workflow`

Workflow automation and monitoring commands.

```
hubqueue workflow [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue workflow list`

List GitHub Actions workflows for a repository.

```
hubqueue workflow list [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow trigger`

Trigger a GitHub Actions workflow run.

```
hubqueue workflow trigger [OPTIONS] REPO_NAME WORKFLOW_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `WORKFLOW_ID`: Workflow ID or file name

Options:
- `--ref`: Git reference (branch, tag, SHA) (default: main)
- `--input`: Workflow input in format 'key=value' (can be specified multiple times)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--monitor`: Monitor workflow run until completion
- `--interval`: Polling interval in seconds for monitoring (default: 5)
- `--timeout`: Timeout in seconds for monitoring (default: 300)

#### `hubqueue workflow runs`

List GitHub Actions workflow runs for a repository.

```
hubqueue workflow runs [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--workflow`: Filter by workflow ID or file name
- `--status`: Filter by status (queued, in_progress, completed)
- `--branch`: Filter by branch name
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow view`

View detailed information about a workflow run.

```
hubqueue workflow view [OPTIONS] REPO_NAME RUN_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `RUN_ID`: Workflow run ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow cancel`

Cancel a workflow run.

```
hubqueue workflow cancel [OPTIONS] REPO_NAME RUN_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `RUN_ID`: Workflow run ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow rerun`

Rerun a workflow run.

```
hubqueue workflow rerun [OPTIONS] REPO_NAME RUN_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `RUN_ID`: Workflow run ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow secrets`

List repository secrets.

```
hubqueue workflow secrets [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow set-secret`

Create or update a repository secret.

```
hubqueue workflow set-secret [OPTIONS] REPO_NAME SECRET_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `SECRET_NAME`: Secret name

Options:
- `--value`: Secret value (will prompt if not provided)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow delete-secret`

Delete a repository secret.

```
hubqueue workflow delete-secret [OPTIONS] REPO_NAME SECRET_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `SECRET_NAME`: Secret name

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow caches`

List GitHub Actions caches for a repository.

```
hubqueue workflow caches [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue workflow delete-cache`

Delete a GitHub Actions cache.

```
hubqueue workflow delete-cache [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--id`: Cache ID to delete
- `--key`: Cache key to delete
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)