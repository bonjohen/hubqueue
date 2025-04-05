"""
Wizard module for HubQueue.
"""
import os
import sys
import json
import time
from typing import List, Dict, Any, Optional, Callable, Union
from .ui import (
    Color, print_color, print_header, print_info, print_success,
    print_warning, print_error, prompt, confirm, select, multi_select,
    password, clear_screen, is_interactive
)
from .logging import get_logger

# Get logger
logger = get_logger()


class Wizard:
    """Base wizard class for interactive workflows."""
    
    def __init__(self, title="Wizard", description=None, steps=None):
        """
        Initialize a wizard.
        
        Args:
            title (str, optional): Wizard title. Defaults to "Wizard".
            description (str, optional): Wizard description. Defaults to None.
            steps (List[str], optional): Wizard steps. Defaults to None.
        """
        self.title = title
        self.description = description
        self.steps = steps or []
        self.current_step = 0
        self.data = {}
        self.cancelled = False
    
    def run(self):
        """
        Run the wizard.
        
        Returns:
            Dict[str, Any]: Wizard data
        """
        if not is_interactive():
            logger.warning("Wizard cannot run in non-interactive mode")
            return self.data
        
        try:
            # Display wizard header
            self._display_header()
            
            # Run wizard steps
            while self.current_step < len(self.steps):
                step_name = self.steps[self.current_step]
                step_method = getattr(self, f"step_{step_name}", None)
                
                if step_method:
                    # Display step header
                    self._display_step_header(step_name)
                    
                    # Run step
                    result = step_method()
                    
                    # Check if step was cancelled
                    if result is False:
                        if confirm("Are you sure you want to cancel the wizard?"):
                            self.cancelled = True
                            break
                        else:
                            continue
                    
                    # Move to next step
                    self.current_step += 1
                else:
                    logger.error(f"Step method not found: step_{step_name}")
                    self.current_step += 1
            
            # Display wizard footer
            if not self.cancelled:
                self._display_footer()
            else:
                print_warning("Wizard cancelled.")
            
            return self.data
        except KeyboardInterrupt:
            print_warning("\nWizard cancelled.")
            self.cancelled = True
            return self.data
    
    def _display_header(self):
        """Display wizard header."""
        clear_screen()
        print_header(self.title)
        
        if self.description:
            print_info(self.description)
            print_color("")
    
    def _display_step_header(self, step_name):
        """
        Display step header.
        
        Args:
            step_name (str): Step name
        """
        step_index = self.current_step + 1
        step_title = step_name.replace("_", " ").title()
        
        print_color("")
        print_color(f"Step {step_index}/{len(self.steps)}: {step_title}", Color.CYAN, bold=True)
        print_color("-" * 40, Color.CYAN)
    
    def _display_footer(self):
        """Display wizard footer."""
        print_color("")
        print_success(f"{self.title} completed successfully!")


class RepositoryWizard(Wizard):
    """Wizard for creating a new repository."""
    
    def __init__(self):
        """Initialize repository wizard."""
        super().__init__(
            title="Repository Creation Wizard",
            description="This wizard will guide you through creating a new GitHub repository.",
            steps=[
                "repository_info",
                "repository_settings",
                "repository_files",
                "repository_collaborators",
                "repository_confirmation",
            ]
        )
    
    def step_repository_info(self):
        """
        Step 1: Repository information.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Enter basic information about your repository.")
        
        # Get repository name
        name = prompt("Repository name", validate=lambda x: x and "/" not in x)
        
        # Get repository owner
        owner_type = select("Repository owner type", ["Personal", "Organization"])
        
        if owner_type == "Organization":
            owner = prompt("Organization name")
        else:
            owner = prompt("Username")
        
        # Get repository description
        description = prompt("Repository description (optional)", default="")
        
        # Get repository visibility
        visibility = select("Repository visibility", ["Public", "Private"], default="Public")
        
        # Save data
        self.data["name"] = name
        self.data["owner"] = owner
        self.data["owner_type"] = owner_type
        self.data["description"] = description
        self.data["visibility"] = visibility.lower()
        
        return True
    
    def step_repository_settings(self):
        """
        Step 2: Repository settings.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Configure repository settings.")
        
        # Get repository features
        features = multi_select(
            "Select repository features",
            [
                "Issues",
                "Projects",
                "Wiki",
                "Discussions",
                "Allow squash merging",
                "Allow merge commits",
                "Allow rebase merging",
                "Automatically delete head branches",
            ],
            defaults=[
                "Issues",
                "Projects",
                "Wiki",
                "Allow squash merging",
                "Allow merge commits",
                "Allow rebase merging",
            ]
        )
        
        # Get default branch
        default_branch = prompt("Default branch name", default="main")
        
        # Save data
        self.data["features"] = features
        self.data["default_branch"] = default_branch
        
        return True
    
    def step_repository_files(self):
        """
        Step 3: Repository files.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Configure initial repository files.")
        
        # Get README
        create_readme = confirm("Create README.md?", default=True)
        
        if create_readme:
            readme_template = select(
                "README template",
                ["Basic", "Standard", "Detailed"],
                default="Standard"
            )
        else:
            readme_template = None
        
        # Get .gitignore
        create_gitignore = confirm("Create .gitignore?", default=True)
        
        if create_gitignore:
            gitignore_template = select(
                "Select .gitignore template",
                [
                    "None (empty)",
                    "Python",
                    "Node",
                    "Java",
                    "C++",
                    "Go",
                    "Ruby",
                    "Rust",
                ],
                default="None (empty)"
            )
            
            if gitignore_template == "None (empty)":
                gitignore_template = None
        else:
            gitignore_template = None
        
        # Get license
        create_license = confirm("Create LICENSE?", default=True)
        
        if create_license:
            license_template = select(
                "Select license template",
                [
                    "MIT",
                    "Apache-2.0",
                    "GPL-3.0",
                    "BSD-3-Clause",
                    "AGPL-3.0",
                    "MPL-2.0",
                    "Unlicense",
                ],
                default="MIT"
            )
        else:
            license_template = None
        
        # Save data
        self.data["create_readme"] = create_readme
        self.data["readme_template"] = readme_template
        self.data["create_gitignore"] = create_gitignore
        self.data["gitignore_template"] = gitignore_template
        self.data["create_license"] = create_license
        self.data["license_template"] = license_template
        
        return True
    
    def step_repository_collaborators(self):
        """
        Step 4: Repository collaborators.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Add collaborators to your repository.")
        
        # Ask if user wants to add collaborators
        add_collaborators = confirm("Do you want to add collaborators?", default=False)
        
        if add_collaborators:
            collaborators = []
            
            while True:
                # Get collaborator username
                username = prompt("Collaborator username")
                
                # Get collaborator permission
                permission = select(
                    "Collaborator permission",
                    ["Read", "Triage", "Write", "Maintain", "Admin"],
                    default="Write"
                )
                
                # Add collaborator
                collaborators.append({
                    "username": username,
                    "permission": permission.lower(),
                })
                
                # Ask if user wants to add another collaborator
                if not confirm("Add another collaborator?", default=False):
                    break
        else:
            collaborators = []
        
        # Save data
        self.data["collaborators"] = collaborators
        
        return True
    
    def step_repository_confirmation(self):
        """
        Step 5: Repository confirmation.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Review repository configuration.")
        
        # Display repository information
        print_color("\nRepository Information:", Color.CYAN, bold=True)
        print_color(f"Name: {self.data['name']}")
        print_color(f"Owner: {self.data['owner']} ({self.data['owner_type']})")
        print_color(f"Description: {self.data['description'] or 'None'}")
        print_color(f"Visibility: {self.data['visibility']}")
        
        # Display repository settings
        print_color("\nRepository Settings:", Color.CYAN, bold=True)
        print_color(f"Default Branch: {self.data['default_branch']}")
        print_color("Features:")
        for feature in self.data["features"]:
            print_color(f"- {feature}")
        
        # Display repository files
        print_color("\nRepository Files:", Color.CYAN, bold=True)
        print_color(f"README.md: {'Yes' if self.data['create_readme'] else 'No'}")
        if self.data["create_readme"]:
            print_color(f"README Template: {self.data['readme_template']}")
        
        print_color(f".gitignore: {'Yes' if self.data['create_gitignore'] else 'No'}")
        if self.data["create_gitignore"] and self.data["gitignore_template"]:
            print_color(f".gitignore Template: {self.data['gitignore_template']}")
        
        print_color(f"LICENSE: {'Yes' if self.data['create_license'] else 'No'}")
        if self.data["create_license"]:
            print_color(f"License Template: {self.data['license_template']}")
        
        # Display collaborators
        print_color("\nCollaborators:", Color.CYAN, bold=True)
        if self.data["collaborators"]:
            for collaborator in self.data["collaborators"]:
                print_color(f"- {collaborator['username']} ({collaborator['permission']})")
        else:
            print_color("None")
        
        # Confirm repository creation
        print_color("")
        return confirm("Create repository with these settings?", default=True)


class IssueWizard(Wizard):
    """Wizard for creating a new issue."""
    
    def __init__(self, repo_name=None):
        """
        Initialize issue wizard.
        
        Args:
            repo_name (str, optional): Repository name. Defaults to None.
        """
        super().__init__(
            title="Issue Creation Wizard",
            description="This wizard will guide you through creating a new GitHub issue.",
            steps=[
                "repository",
                "issue_info",
                "issue_details",
                "issue_confirmation",
            ]
        )
        
        self.data["repo_name"] = repo_name
    
    def step_repository(self):
        """
        Step 1: Repository selection.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        # Skip if repository is already provided
        if self.data.get("repo_name"):
            return True
        
        print_info("Select the repository for the issue.")
        
        # Get repository name
        repo_name = prompt("Repository name (owner/repo)")
        
        # Save data
        self.data["repo_name"] = repo_name
        
        return True
    
    def step_issue_info(self):
        """
        Step 2: Issue information.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Enter basic information about the issue.")
        
        # Get issue title
        title = prompt("Issue title")
        
        # Get issue type
        issue_type = select(
            "Issue type",
            ["Bug", "Feature", "Documentation", "Question", "Other"],
            default="Bug"
        )
        
        # Get issue priority
        priority = select(
            "Issue priority",
            ["Low", "Medium", "High", "Critical"],
            default="Medium"
        )
        
        # Save data
        self.data["title"] = title
        self.data["type"] = issue_type
        self.data["priority"] = priority
        
        return True
    
    def step_issue_details(self):
        """
        Step 3: Issue details.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Enter detailed information about the issue.")
        
        # Get issue description
        if self.data["type"] == "Bug":
            description_template = (
                "## Description\n"
                "A clear and concise description of the bug.\n\n"
                "## Steps to Reproduce\n"
                "1. Step 1\n"
                "2. Step 2\n"
                "3. Step 3\n\n"
                "## Expected Behavior\n"
                "A clear and concise description of what you expected to happen.\n\n"
                "## Actual Behavior\n"
                "A clear and concise description of what actually happened.\n\n"
                "## Environment\n"
                "- OS: [e.g. Windows 10, macOS 12.0]\n"
                "- Browser/Version: [e.g. Chrome 96.0.4664.110]\n"
                "- Other relevant environment details\n\n"
                "## Additional Information\n"
                "Any additional information, screenshots, or context about the problem."
            )
        elif self.data["type"] == "Feature":
            description_template = (
                "## Description\n"
                "A clear and concise description of the feature request.\n\n"
                "## Problem Statement\n"
                "A clear and concise description of the problem this feature would solve.\n\n"
                "## Proposed Solution\n"
                "A clear and concise description of what you want to happen.\n\n"
                "## Alternatives Considered\n"
                "A clear and concise description of any alternative solutions or features you've considered.\n\n"
                "## Additional Information\n"
                "Any additional information, screenshots, or context about the feature request."
            )
        else:
            description_template = (
                "## Description\n"
                "A clear and concise description of the issue.\n\n"
                "## Additional Information\n"
                "Any additional information or context about the issue."
            )
        
        print_info("Enter issue description (an editor will open):")
        description = prompt("Press Enter to open editor, or type description here", default="")
        
        if not description:
            from .config import edit_file
            description = edit_file(None, initial_content=description_template)
        
        # Get issue labels
        labels = multi_select(
            "Select issue labels",
            [
                f"type:{self.data['type'].lower()}",
                f"priority:{self.data['priority'].lower()}",
                "good first issue",
                "help wanted",
                "duplicate",
                "wontfix",
                "invalid",
            ],
            defaults=[
                f"type:{self.data['type'].lower()}",
                f"priority:{self.data['priority'].lower()}",
            ]
        )
        
        # Get issue assignees
        add_assignees = confirm("Do you want to add assignees?", default=False)
        
        if add_assignees:
            assignees = []
            
            while True:
                # Get assignee username
                username = prompt("Assignee username")
                
                # Add assignee
                assignees.append(username)
                
                # Ask if user wants to add another assignee
                if not confirm("Add another assignee?", default=False):
                    break
        else:
            assignees = []
        
        # Save data
        self.data["description"] = description
        self.data["labels"] = labels
        self.data["assignees"] = assignees
        
        return True
    
    def step_issue_confirmation(self):
        """
        Step 4: Issue confirmation.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Review issue configuration.")
        
        # Display issue information
        print_color("\nIssue Information:", Color.CYAN, bold=True)
        print_color(f"Repository: {self.data['repo_name']}")
        print_color(f"Title: {self.data['title']}")
        print_color(f"Type: {self.data['type']}")
        print_color(f"Priority: {self.data['priority']}")
        
        # Display issue details
        print_color("\nIssue Details:", Color.CYAN, bold=True)
        print_color("Description:")
        print_color("-" * 40)
        print_color(self.data["description"][:200] + ("..." if len(self.data["description"]) > 200 else ""))
        print_color("-" * 40)
        
        print_color("Labels:")
        for label in self.data["labels"]:
            print_color(f"- {label}")
        
        print_color("Assignees:")
        if self.data["assignees"]:
            for assignee in self.data["assignees"]:
                print_color(f"- {assignee}")
        else:
            print_color("None")
        
        # Confirm issue creation
        print_color("")
        return confirm("Create issue with these settings?", default=True)


class ReleaseWizard(Wizard):
    """Wizard for creating a new release."""
    
    def __init__(self, repo_name=None):
        """
        Initialize release wizard.
        
        Args:
            repo_name (str, optional): Repository name. Defaults to None.
        """
        super().__init__(
            title="Release Creation Wizard",
            description="This wizard will guide you through creating a new GitHub release.",
            steps=[
                "repository",
                "release_info",
                "release_assets",
                "release_confirmation",
            ]
        )
        
        self.data["repo_name"] = repo_name
    
    def step_repository(self):
        """
        Step 1: Repository selection.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        # Skip if repository is already provided
        if self.data.get("repo_name"):
            return True
        
        print_info("Select the repository for the release.")
        
        # Get repository name
        repo_name = prompt("Repository name (owner/repo)")
        
        # Save data
        self.data["repo_name"] = repo_name
        
        return True
    
    def step_release_info(self):
        """
        Step 2: Release information.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Enter basic information about the release.")
        
        # Get release tag
        tag = prompt("Release tag (e.g., v1.0.0)")
        
        # Get release title
        title = prompt("Release title", default=tag)
        
        # Get release target
        target = prompt("Target branch or commit", default="main")
        
        # Get release type
        release_type = select(
            "Release type",
            ["Full Release", "Pre-release", "Draft"],
            default="Full Release"
        )
        
        # Get release notes
        generate_notes = confirm("Generate release notes automatically?", default=True)
        
        if generate_notes:
            notes = None
        else:
            print_info("Enter release notes (an editor will open):")
            notes = prompt("Press Enter to open editor, or type notes here", default="")
            
            if not notes:
                from .config import edit_file
                notes_template = (
                    "## What's New\n"
                    "- Feature 1\n"
                    "- Feature 2\n\n"
                    "## Bug Fixes\n"
                    "- Bug fix 1\n"
                    "- Bug fix 2\n\n"
                    "## Breaking Changes\n"
                    "- Breaking change 1\n\n"
                    "## Additional Information\n"
                    "Any additional information about the release."
                )
                notes = edit_file(None, initial_content=notes_template)
        
        # Save data
        self.data["tag"] = tag
        self.data["title"] = title
        self.data["target"] = target
        self.data["type"] = release_type
        self.data["generate_notes"] = generate_notes
        self.data["notes"] = notes
        
        return True
    
    def step_release_assets(self):
        """
        Step 3: Release assets.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Add assets to the release.")
        
        # Ask if user wants to add assets
        add_assets = confirm("Do you want to add assets to the release?", default=False)
        
        if add_assets:
            assets = []
            
            while True:
                # Get asset path
                path = prompt("Asset file path")
                
                # Get asset label
                label = prompt("Asset label (optional)", default="")
                
                # Add asset
                assets.append({
                    "path": path,
                    "label": label,
                })
                
                # Ask if user wants to add another asset
                if not confirm("Add another asset?", default=False):
                    break
        else:
            assets = []
        
        # Save data
        self.data["assets"] = assets
        
        return True
    
    def step_release_confirmation(self):
        """
        Step 4: Release confirmation.
        
        Returns:
            bool: True if step completed, False if cancelled
        """
        print_info("Review release configuration.")
        
        # Display release information
        print_color("\nRelease Information:", Color.CYAN, bold=True)
        print_color(f"Repository: {self.data['repo_name']}")
        print_color(f"Tag: {self.data['tag']}")
        print_color(f"Title: {self.data['title']}")
        print_color(f"Target: {self.data['target']}")
        print_color(f"Type: {self.data['type']}")
        
        # Display release notes
        print_color("\nRelease Notes:", Color.CYAN, bold=True)
        if self.data["generate_notes"]:
            print_color("Auto-generated from commits")
        else:
            print_color("-" * 40)
            print_color(self.data["notes"][:200] + ("..." if len(self.data["notes"]) > 200 else ""))
            print_color("-" * 40)
        
        # Display release assets
        print_color("\nRelease Assets:", Color.CYAN, bold=True)
        if self.data["assets"]:
            for asset in self.data["assets"]:
                label_str = f" ({asset['label']})" if asset["label"] else ""
                print_color(f"- {asset['path']}{label_str}")
        else:
            print_color("None")
        
        # Confirm release creation
        print_color("")
        return confirm("Create release with these settings?", default=True)


def run_repository_wizard():
    """
    Run the repository creation wizard.
    
    Returns:
        Dict[str, Any]: Wizard data
    """
    wizard = RepositoryWizard()
    return wizard.run()


def run_issue_wizard(repo_name=None):
    """
    Run the issue creation wizard.
    
    Args:
        repo_name (str, optional): Repository name. Defaults to None.
        
    Returns:
        Dict[str, Any]: Wizard data
    """
    wizard = IssueWizard(repo_name)
    return wizard.run()


def run_release_wizard(repo_name=None):
    """
    Run the release creation wizard.
    
    Args:
        repo_name (str, optional): Repository name. Defaults to None.
        
    Returns:
        Dict[str, Any]: Wizard data
    """
    wizard = ReleaseWizard(repo_name)
    return wizard.run()
