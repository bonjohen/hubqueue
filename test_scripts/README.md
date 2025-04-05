# HubQueue Test Scripts

This directory contains test scripts that demonstrate the functionality of HubQueue. These scripts are designed to be run outside of the project and GitHub environment, allowing you to test HubQueue in your own environment.

## Available Scripts

### Windows Scripts

1. **test_hub.cmd** - Basic test script that demonstrates the core functionality of HubQueue.
2. **test_hub_simple.cmd** - Simplified test script that focuses on the most common operations.
3. **test_hub_comprehensive.cmd** - Comprehensive test script that demonstrates all the functionality of HubQueue.

### Linux/macOS Scripts

1. **test_hub_simple.sh** - Simplified test script for Linux/macOS that focuses on the most common operations.
2. **test_hub_comprehensive.sh** - Comprehensive test script for Linux/macOS that demonstrates all the functionality of HubQueue.

## Prerequisites

Before running these scripts, make sure you have:

1. Python 3.6 or higher installed
2. A GitHub account
3. A GitHub personal access token with the following scopes:
   - `repo` (Full control of private repositories)
   - `user` (Update all user data)
   - `admin:org` (Full control of orgs and teams)
   - `delete_repo` (Delete repositories)

## Setting Up Your Environment

1. Set your GitHub token as an environment variable:

   **Windows:**
   ```
   set GITHUB_TOKEN=your_token_here
   ```

   **Linux/macOS:**
   ```
   export GITHUB_TOKEN=your_token_here
   ```

2. Clone the HubQueue repository:
   ```
   git clone https://github.com/yourusername/hubqueue.git
   cd hubqueue
   ```

3. Make the scripts executable (Linux/macOS only):
   ```
   chmod +x test_scripts/test_hub_simple.sh
   chmod +x test_scripts/test_hub_comprehensive.sh
   ```

## Running the Scripts

### Windows

1. Open Command Prompt
2. Navigate to the HubQueue directory
3. Run one of the scripts:
   ```
   test_scripts\test_hub.cmd
   ```
   or
   ```
   test_scripts\test_hub_simple.cmd
   ```
   or
   ```
   test_scripts\test_hub_comprehensive.cmd
   ```

### Linux/macOS

1. Open Terminal
2. Navigate to the HubQueue directory
3. Run one of the scripts:
   ```
   ./test_scripts/test_hub_simple.sh
   ```
   or
   ```
   ./test_scripts/test_hub_comprehensive.sh
   ```

## What the Scripts Do

These scripts demonstrate various HubQueue operations, including:

1. **Repository Management** - Creating, listing, updating, and deleting repositories
2. **Branch Operations** - Creating branches, setting default branches, and managing branch protection
3. **Issue Tracking** - Creating, listing, updating, and commenting on issues
4. **Pull Requests** - Creating, listing, updating, and commenting on pull requests
5. **Release Management** - Creating, listing, and updating releases
6. **Collaboration** - Managing collaborators
7. **Project Management** - Creating and listing projects
8. **Gist Management** - Creating and listing gists
9. **Notifications** - Listing and marking notifications as read
10. **Interactive Features** - UI customization, wizards, forms, and error handling

## Cleanup

At the end of each script, you'll be asked if you want to delete the test repository. If you choose not to delete it, you can manually delete it later using:

```
hubqueue repository delete test-hubqueue-demo --confirm
```

or

```
hubqueue repository delete test-hubqueue-simple --confirm
```

## Troubleshooting

If you encounter any issues:

1. Make sure your GitHub token has the required scopes
2. Check that Python and pip are properly installed
3. Ensure you're running the scripts from the HubQueue directory
4. Try running the commands manually to see more detailed error messages

## Note

These scripts create real repositories, issues, and other resources in your GitHub account. While they attempt to clean up after themselves, make sure you understand what they're doing before running them.
