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

## Gist Management Commands

### `hubqueue gist`

Gist management commands.

```
hubqueue gist [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue gist list`

List GitHub Gists for the authenticated user.

```
hubqueue gist list [OPTIONS]
```

Options:
- `--public`: List only public gists
- `--starred`: List starred gists instead of owned gists
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--format`: Output format (table, simple) (default: simple)

#### `hubqueue gist view`

View detailed information about a gist.

```
hubqueue gist view [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--raw`: Show raw file content

#### `hubqueue gist create`

Create a new gist.

```
hubqueue gist create [OPTIONS]
```

Options:
- `--file`: File to include (can be specified multiple times)
- `--content`: File content in format 'filename:content' (can be specified multiple times)
- `--description`: Gist description
- `--public/--private`: Whether the gist is public (default: private)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist update`

Update an existing gist.

```
hubqueue gist update [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--file`: File to update (can be specified multiple times)
- `--content`: File content in format 'filename:content' (can be specified multiple times)
- `--description`: New gist description
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist delete`

Delete a gist.

```
hubqueue gist delete [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue gist star`

Star a gist.

```
hubqueue gist star [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist unstar`

Unstar a gist.

```
hubqueue gist unstar [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist comment`

Add a comment to a gist.

```
hubqueue gist comment [OPTIONS] GIST_ID BODY
```

Arguments:
- `GIST_ID`: Gist ID
- `BODY`: Comment body

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist delete-comment`

Delete a comment from a gist.

```
hubqueue gist delete-comment [OPTIONS] GIST_ID COMMENT_ID
```

Arguments:
- `GIST_ID`: Gist ID
- `COMMENT_ID`: Comment ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue gist fork`

Fork a gist.

```
hubqueue gist fork [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist download`

Download a gist to the local filesystem.

```
hubqueue gist download [OPTIONS] GIST_ID
```

Arguments:
- `GIST_ID`: Gist ID

Options:
- `--directory`: Directory to save files to (default: current directory)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue gist upload`

Upload files to a new gist.

```
hubqueue gist upload [OPTIONS] FILES_OR_DIRECTORY...
```

Arguments:
- `FILES_OR_DIRECTORY`: Files or directory to upload

Options:
- `--description`: Gist description
- `--public/--private`: Whether the gist is public (default: private)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

## Project Templates Commands

### `hubqueue template`

Project templates and scaffolding commands.

```
hubqueue template [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue template list`

List available project templates.

```
hubqueue template list [OPTIONS]
```

Options:
- `--templates-dir`: Directory containing templates
- `--format`: Output format (table, simple) (default: simple)

#### `hubqueue template view`

View detailed information about a template.

```
hubqueue template view [OPTIONS] TEMPLATE_NAME
```

Arguments:
- `TEMPLATE_NAME`: Template name

Options:
- `--templates-dir`: Directory containing templates
- `--show-variables`: Show template variables

#### `hubqueue template create`

Create a new template from a directory.

```
hubqueue template create [OPTIONS] NAME SOURCE_DIR
```

Arguments:
- `NAME`: Template name
- `SOURCE_DIR`: Source directory containing template files

Options:
- `--description`: Template description
- `--version`: Template version (default: 1.0.0)
- `--templates-dir`: Directory to save template to

#### `hubqueue template delete`

Delete a template.

```
hubqueue template delete [OPTIONS] TEMPLATE_NAME
```

Arguments:
- `TEMPLATE_NAME`: Template name

Options:
- `--templates-dir`: Directory containing templates
- `--confirm`: Skip confirmation prompt

#### `hubqueue template import-github`

Import a template from a GitHub repository.

```
hubqueue template import-github [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--path`: Path within repository to use as template
- `--name`: Template name (default: repository name)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--templates-dir`: Directory to save template to

#### `hubqueue template import-url`

Import a template from a URL.

```
hubqueue template import-url [OPTIONS] URL NAME
```

Arguments:
- `URL`: URL to zip file containing template
- `NAME`: Template name

Options:
- `--description`: Template description
- `--templates-dir`: Directory to save template to

#### `hubqueue template generate`

Generate a project from a template.

```
hubqueue template generate [OPTIONS] TEMPLATE_NAME OUTPUT_DIR
```

Arguments:
- `TEMPLATE_NAME`: Template name
- `OUTPUT_DIR`: Output directory

Options:
- `--var`: Template variable in format 'name=value' (can be specified multiple times)
- `--templates-dir`: Directory containing templates

#### `hubqueue template variables`

List variables for a template.

```
hubqueue template variables [OPTIONS] TEMPLATE_NAME
```

Arguments:
- `TEMPLATE_NAME`: Template name

Options:
- `--templates-dir`: Directory containing templates

## Project Management Commands

### `hubqueue project`

Project management commands.

```
hubqueue project [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue project list`

List project boards for a repository.

```
hubqueue project list [OPTIONS] REPO_NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--format`: Output format (table, simple) (default: simple)

#### `hubqueue project view`

View detailed information about a project board.

```
hubqueue project view [OPTIONS] REPO_NAME PROJECT_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project create`

Create a new project board.

```
hubqueue project create [OPTIONS] REPO_NAME NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `NAME`: Project name

Options:
- `--body`: Project description
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project create-from-template`

Create a project board from a template.

```
hubqueue project create-from-template [OPTIONS] REPO_NAME NAME TEMPLATE
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `NAME`: Project name
- `TEMPLATE`: Template name (basic, automated, bug_triage)

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project add-column`

Add a column to a project board.

```
hubqueue project add-column [OPTIONS] REPO_NAME PROJECT_ID NAME
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `NAME`: Column name

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project add-issue`

Add an issue to a project board column.

```
hubqueue project add-issue [OPTIONS] REPO_NAME PROJECT_ID COLUMN_ID ISSUE_NUMBER
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `COLUMN_ID`: Column ID
- `ISSUE_NUMBER`: Issue number

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project add-pr`

Add a pull request to a project board column.

```
hubqueue project add-pr [OPTIONS] REPO_NAME PROJECT_ID COLUMN_ID PR_NUMBER
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `COLUMN_ID`: Column ID
- `PR_NUMBER`: Pull request number

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project add-note`

Add a note to a project board column.

```
hubqueue project add-note [OPTIONS] REPO_NAME PROJECT_ID COLUMN_ID NOTE
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `COLUMN_ID`: Column ID
- `NOTE`: Note content

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project move-card`

Move a card to a different column or position.

```
hubqueue project move-card [OPTIONS] REPO_NAME PROJECT_ID CARD_ID COLUMN_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `CARD_ID`: Card ID
- `COLUMN_ID`: Target column ID

Options:
- `--position`: Position in column (top, bottom) (default: top)
- `--after`: Position card after this card ID
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue project delete-card`

Delete a card from a project board.

```
hubqueue project delete-card [OPTIONS] REPO_NAME PROJECT_ID CARD_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `CARD_ID`: Card ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue project delete-column`

Delete a column from a project board.

```
hubqueue project delete-column [OPTIONS] REPO_NAME PROJECT_ID COLUMN_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID
- `COLUMN_ID`: Column ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue project delete`

Delete a project board.

```
hubqueue project delete [OPTIONS] REPO_NAME PROJECT_ID
```

Arguments:
- `REPO_NAME`: Repository name in format 'owner/repo'
- `PROJECT_ID`: Project ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

## System Management Commands

### `hubqueue system`

System and environment management commands.

```
hubqueue system [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue system info`

Get system information.

```
hubqueue system info [OPTIONS]
```

Options:
- `--output`: Output file path
- `--format`: Output format (json, table) (default: table)

#### `hubqueue system check-dependencies`

Check dependencies required by HubQueue.

```
hubqueue system check-dependencies [OPTIONS]
```

Options:
- `--install-missing`: Install missing dependencies
- `--upgrade`: Upgrade dependencies when installing

#### `hubqueue system git-config`

Check or set Git configuration.

```
hubqueue system git-config [OPTIONS]
```

Options:
- `--set`: Set Git configuration
- `--key`: Configuration key (required with --set)
- `--value`: Configuration value (required with --set)
- `--global/--local`: Set global or local configuration (default: global)

#### `hubqueue system setup`

Setup environment for HubQueue.

```
hubqueue system setup [OPTIONS]
```

Options:
- `--force`: Force setup even if already configured

#### `hubqueue system export`

Export environment information to a file.

```
hubqueue system export [OPTIONS]
```

Options:
- `--output`: Output file path

#### `hubqueue system check-updates`

Check for updates to HubQueue.

```
hubqueue system check-updates [OPTIONS]
```

Options:
- `--install`: Install updates if available

#### `hubqueue system windows-compatibility`

Check Windows compatibility.

```
hubqueue system windows-compatibility [OPTIONS]
```

Options:
- `--setup`: Setup Windows environment

## SSH Key Management Commands

### `hubqueue ssh`

SSH key management commands.

```
hubqueue ssh [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue ssh list`

List SSH keys.

```
hubqueue ssh list [OPTIONS]
```

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--local`: List local SSH keys instead of GitHub keys
- `--ssh-dir`: SSH directory (default: ~/.ssh)
- `--format`: Output format (table, simple) (default: simple)

#### `hubqueue ssh generate`

Generate a new SSH key.

```
hubqueue ssh generate [OPTIONS] NAME
```

Arguments:
- `NAME`: Key name

Options:
- `--passphrase`: Key passphrase
- `--type`: Key type (rsa, ed25519) (default: rsa)
- `--bits`: Key bits (for RSA keys, default: 4096)
- `--ssh-dir`: SSH directory (default: ~/.ssh)
- `--upload`: Upload key to GitHub after generation
- `--token`: GitHub API token (required with --upload)

## Interactive Wizard Commands

### `hubqueue wizard`

Interactive wizards for common tasks.

```
hubqueue wizard [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue wizard repository`

Run the repository creation wizard.

```
hubqueue wizard repository [OPTIONS]
```

#### `hubqueue wizard issue`

Run the issue creation wizard.

```
hubqueue wizard issue [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'

#### `hubqueue wizard release`

Run the release creation wizard.

```
hubqueue wizard release [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'

## Interactive Form Commands

### `hubqueue form`

Interactive forms for common tasks.

```
hubqueue form [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue form repository`

Run the repository creation form.

```
hubqueue form repository [OPTIONS]
```

#### `hubqueue form issue`

Run the issue creation form.

```
hubqueue form issue [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'

## UI Commands

### `hubqueue ui`

User interface commands.

```
hubqueue ui [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue ui color`

Enable or disable color output.

```
hubqueue ui color [OPTIONS]
```

Options:
- `--enable/--disable`: Enable or disable color output (default: enable)

#### `hubqueue ui interactive`

Enable or disable interactive mode.

```
hubqueue ui interactive [OPTIONS]
```

Options:
- `--enable/--disable`: Enable or disable interactive mode (default: enable)

#### `hubqueue ui clear`

Clear the terminal screen.

```
hubqueue ui clear [OPTIONS]
```

#### `hubqueue ssh upload`

Upload an SSH key to GitHub.

```
hubqueue ssh upload [OPTIONS] KEY_PATH
```

Arguments:
- `KEY_PATH`: Path to public key file

Options:
- `--title`: Key title (default: filename)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue ssh delete`

Delete an SSH key from GitHub.

```
hubqueue ssh delete [OPTIONS] KEY_ID
```

Arguments:
- `KEY_ID`: Key ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue ssh validate`

Validate an SSH key.

```
hubqueue ssh validate [OPTIONS] KEY_PATH
```

Arguments:
- `KEY_PATH`: Path to key file

## Notification Management Commands

### `hubqueue notification`

Notification management commands.

```
hubqueue notification [OPTIONS] COMMAND [ARGS]...
```

#### `hubqueue notification list`

List notifications.

```
hubqueue notification list [OPTIONS]
```

Options:
- `--all`: Show all notifications, including ones marked as read
- `--participating`: Only show notifications in which the user is directly participating or mentioned
- `--since`: Only show notifications updated after the given time (ISO 8601 format)
- `--before`: Only show notifications updated before the given time (ISO 8601 format)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--format`: Output format (table, simple) (default: simple)

#### `hubqueue notification view`

View detailed information about a notification.

```
hubqueue notification view [OPTIONS] NOTIFICATION_ID
```

Arguments:
- `NOTIFICATION_ID`: Notification ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue notification mark-read`

Mark a notification as read.

```
hubqueue notification mark-read [OPTIONS] NOTIFICATION_ID
```

Arguments:
- `NOTIFICATION_ID`: Notification ID

Options:
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue notification mark-all-read`

Mark all notifications as read.

```
hubqueue notification mark-all-read [OPTIONS]
```

Options:
- `--repo`: Repository name in format 'owner/repo'
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)
- `--confirm`: Skip confirmation prompt

#### `hubqueue notification subscribe`

Subscribe to a notification thread.

```
hubqueue notification subscribe [OPTIONS] NOTIFICATION_ID
```

Arguments:
- `NOTIFICATION_ID`: Notification ID

Options:
- `--ignore`: Ignore the thread instead of subscribing
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)

#### `hubqueue notification poll`

Poll for new notifications.

```
hubqueue notification poll [OPTIONS]
```

Options:
- `--interval`: Polling interval in seconds (default: 60)
- `--token`: GitHub API token (or set GITHUB_TOKEN env variable)