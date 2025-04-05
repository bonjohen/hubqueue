"""
Forms module for HubQueue.
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


class Field:
    """Base field class for forms."""
    
    def __init__(self, name, label, required=False, default=None, help_text=None, validators=None):
        """
        Initialize a field.
        
        Args:
            name (str): Field name
            label (str): Field label
            required (bool, optional): Whether the field is required. Defaults to False.
            default (Any, optional): Default value. Defaults to None.
            help_text (str, optional): Help text. Defaults to None.
            validators (List[Callable], optional): Validators. Defaults to None.
        """
        self.name = name
        self.label = label
        self.required = required
        self.default = default
        self.help_text = help_text
        self.validators = validators or []
        self.value = None
    
    def get_prompt_text(self):
        """
        Get prompt text.
        
        Returns:
            str: Prompt text
        """
        text = self.label
        if self.required:
            text += " (required)"
        if self.help_text:
            text += f"\n{self.help_text}"
        return text
    
    def validate(self, value):
        """
        Validate field value.
        
        Args:
            value (Any): Field value
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if required
        if self.required and (value is None or value == ""):
            print_error(f"{self.label} is required.")
            return False
        
        # Run validators
        for validator in self.validators:
            if not validator(value):
                return False
        
        return True
    
    def render(self):
        """
        Render field.
        
        Returns:
            Any: Field value
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    def to_dict(self):
        """
        Convert field to dictionary.
        
        Returns:
            Dict[str, Any]: Field dictionary
        """
        return {
            "name": self.name,
            "label": self.label,
            "required": self.required,
            "default": self.default,
            "help_text": self.help_text,
            "value": self.value,
        }


class TextField(Field):
    """Text field for forms."""
    
    def __init__(self, name, label, required=False, default=None, help_text=None, validators=None, min_length=None, max_length=None):
        """
        Initialize a text field.
        
        Args:
            name (str): Field name
            label (str): Field label
            required (bool, optional): Whether the field is required. Defaults to False.
            default (str, optional): Default value. Defaults to None.
            help_text (str, optional): Help text. Defaults to None.
            validators (List[Callable], optional): Validators. Defaults to None.
            min_length (int, optional): Minimum length. Defaults to None.
            max_length (int, optional): Maximum length. Defaults to None.
        """
        super().__init__(name, label, required, default, help_text, validators)
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value):
        """
        Validate field value.
        
        Args:
            value (str): Field value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not super().validate(value):
            return False
        
        # Skip validation if value is None or empty
        if value is None or value == "":
            return True
        
        # Check min length
        if self.min_length is not None and len(value) < self.min_length:
            print_error(f"{self.label} must be at least {self.min_length} characters.")
            return False
        
        # Check max length
        if self.max_length is not None and len(value) > self.max_length:
            print_error(f"{self.label} must be at most {self.max_length} characters.")
            return False
        
        return True
    
    def render(self):
        """
        Render field.
        
        Returns:
            str: Field value
        """
        # Get prompt text
        text = self.get_prompt_text()
        
        # Prompt for value
        while True:
            value = prompt(text, default=self.default)
            
            # Validate value
            if self.validate(value):
                self.value = value
                return value


class PasswordField(TextField):
    """Password field for forms."""
    
    def __init__(self, name, label, required=False, default=None, help_text=None, validators=None, min_length=None, max_length=None, confirmation=True):
        """
        Initialize a password field.
        
        Args:
            name (str): Field name
            label (str): Field label
            required (bool, optional): Whether the field is required. Defaults to False.
            default (str, optional): Default value. Defaults to None.
            help_text (str, optional): Help text. Defaults to None.
            validators (List[Callable], optional): Validators. Defaults to None.
            min_length (int, optional): Minimum length. Defaults to None.
            max_length (int, optional): Maximum length. Defaults to None.
            confirmation (bool, optional): Whether to confirm password. Defaults to True.
        """
        super().__init__(name, label, required, default, help_text, validators, min_length, max_length)
        self.confirmation = confirmation
    
    def render(self):
        """
        Render field.
        
        Returns:
            str: Field value
        """
        # Get prompt text
        text = self.get_prompt_text()
        
        # Prompt for value
        while True:
            value = password(text, confirmation_prompt=self.confirmation)
            
            # Validate value
            if self.validate(value):
                self.value = value
                return value


class BooleanField(Field):
    """Boolean field for forms."""
    
    def render(self):
        """
        Render field.
        
        Returns:
            bool: Field value
        """
        # Get prompt text
        text = self.get_prompt_text()
        
        # Prompt for value
        value = confirm(text, default=self.default or False)
        
        # Validate value
        if self.validate(value):
            self.value = value
            return value


class ChoiceField(Field):
    """Choice field for forms."""
    
    def __init__(self, name, label, choices, required=False, default=None, help_text=None, validators=None):
        """
        Initialize a choice field.
        
        Args:
            name (str): Field name
            label (str): Field label
            choices (List[str]): Choices
            required (bool, optional): Whether the field is required. Defaults to False.
            default (str, optional): Default value. Defaults to None.
            help_text (str, optional): Help text. Defaults to None.
            validators (List[Callable], optional): Validators. Defaults to None.
        """
        super().__init__(name, label, required, default, help_text, validators)
        self.choices = choices
    
    def validate(self, value):
        """
        Validate field value.
        
        Args:
            value (str): Field value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not super().validate(value):
            return False
        
        # Skip validation if value is None or empty
        if value is None or value == "":
            return True
        
        # Check if value is in choices
        if value not in self.choices:
            print_error(f"{self.label} must be one of: {', '.join(self.choices)}.")
            return False
        
        return True
    
    def render(self):
        """
        Render field.
        
        Returns:
            str: Field value
        """
        # Get prompt text
        text = self.get_prompt_text()
        
        # Prompt for value
        value = select(text, self.choices, default=self.default)
        
        # Validate value
        if self.validate(value):
            self.value = value
            return value


class MultiChoiceField(Field):
    """Multi-choice field for forms."""
    
    def __init__(self, name, label, choices, required=False, default=None, help_text=None, validators=None, min_choices=None, max_choices=None):
        """
        Initialize a multi-choice field.
        
        Args:
            name (str): Field name
            label (str): Field label
            choices (List[str]): Choices
            required (bool, optional): Whether the field is required. Defaults to False.
            default (List[str], optional): Default value. Defaults to None.
            help_text (str, optional): Help text. Defaults to None.
            validators (List[Callable], optional): Validators. Defaults to None.
            min_choices (int, optional): Minimum number of choices. Defaults to None.
            max_choices (int, optional): Maximum number of choices. Defaults to None.
        """
        super().__init__(name, label, required, default, help_text, validators)
        self.choices = choices
        self.min_choices = min_choices
        self.max_choices = max_choices
    
    def validate(self, value):
        """
        Validate field value.
        
        Args:
            value (List[str]): Field value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not super().validate(value):
            return False
        
        # Skip validation if value is None or empty
        if value is None or value == []:
            return True
        
        # Check if all values are in choices
        for item in value:
            if item not in self.choices:
                print_error(f"{self.label} must contain only values from: {', '.join(self.choices)}.")
                return False
        
        # Check min choices
        if self.min_choices is not None and len(value) < self.min_choices:
            print_error(f"{self.label} must have at least {self.min_choices} choices.")
            return False
        
        # Check max choices
        if self.max_choices is not None and len(value) > self.max_choices:
            print_error(f"{self.label} must have at most {self.max_choices} choices.")
            return False
        
        return True
    
    def render(self):
        """
        Render field.
        
        Returns:
            List[str]: Field value
        """
        # Get prompt text
        text = self.get_prompt_text()
        
        # Prompt for value
        value = multi_select(text, self.choices, defaults=self.default)
        
        # Validate value
        if self.validate(value):
            self.value = value
            return value


class Form:
    """Base form class."""
    
    def __init__(self, title="Form", description=None, fields=None):
        """
        Initialize a form.
        
        Args:
            title (str, optional): Form title. Defaults to "Form".
            description (str, optional): Form description. Defaults to None.
            fields (List[Field], optional): Form fields. Defaults to None.
        """
        self.title = title
        self.description = description
        self.fields = fields or []
    
    def add_field(self, field):
        """
        Add a field to the form.
        
        Args:
            field (Field): Field to add
        """
        self.fields.append(field)
    
    def render(self):
        """
        Render form.
        
        Returns:
            Dict[str, Any]: Form data
        """
        if not is_interactive():
            logger.warning("Form cannot be rendered in non-interactive mode")
            return {field.name: field.default for field in self.fields}
        
        try:
            # Display form header
            clear_screen()
            print_header(self.title)
            
            if self.description:
                print_info(self.description)
                print_color("")
            
            # Render fields
            data = {}
            for field in self.fields:
                print_color("")
                value = field.render()
                data[field.name] = value
            
            # Display form footer
            print_color("")
            print_success(f"{self.title} completed successfully!")
            
            return data
        except KeyboardInterrupt:
            print_warning("\nForm cancelled.")
            return None
    
    def to_dict(self):
        """
        Convert form to dictionary.
        
        Returns:
            Dict[str, Any]: Form dictionary
        """
        return {
            "title": self.title,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields],
        }


class RepositoryForm(Form):
    """Repository creation form."""
    
    def __init__(self):
        """Initialize repository form."""
        super().__init__(
            title="Repository Creation Form",
            description="Fill out this form to create a new GitHub repository."
        )
        
        # Add fields
        self.add_field(TextField("name", "Repository name", required=True, validators=[
            lambda x: "/" not in x or print_error("Repository name cannot contain '/'.")
        ]))
        
        self.add_field(ChoiceField("owner_type", "Repository owner type", ["Personal", "Organization"], required=True, default="Personal"))
        
        self.add_field(TextField("owner", "Owner name", required=True))
        
        self.add_field(TextField("description", "Repository description"))
        
        self.add_field(ChoiceField("visibility", "Repository visibility", ["Public", "Private"], required=True, default="Public"))
        
        self.add_field(MultiChoiceField("features", "Repository features", [
            "Issues",
            "Projects",
            "Wiki",
            "Discussions",
            "Allow squash merging",
            "Allow merge commits",
            "Allow rebase merging",
            "Automatically delete head branches",
        ], default=[
            "Issues",
            "Projects",
            "Wiki",
            "Allow squash merging",
            "Allow merge commits",
            "Allow rebase merging",
        ]))
        
        self.add_field(TextField("default_branch", "Default branch name", default="main"))
        
        self.add_field(BooleanField("create_readme", "Create README.md?", default=True))
        
        self.add_field(BooleanField("create_gitignore", "Create .gitignore?", default=True))
        
        self.add_field(BooleanField("create_license", "Create LICENSE?", default=True))


class IssueForm(Form):
    """Issue creation form."""
    
    def __init__(self, repo_name=None):
        """
        Initialize issue form.
        
        Args:
            repo_name (str, optional): Repository name. Defaults to None.
        """
        super().__init__(
            title="Issue Creation Form",
            description="Fill out this form to create a new GitHub issue."
        )
        
        # Add fields
        if not repo_name:
            self.add_field(TextField("repo_name", "Repository name (owner/repo)", required=True))
        else:
            self.repo_name = repo_name
        
        self.add_field(TextField("title", "Issue title", required=True))
        
        self.add_field(ChoiceField("type", "Issue type", ["Bug", "Feature", "Documentation", "Question", "Other"], required=True, default="Bug"))
        
        self.add_field(ChoiceField("priority", "Issue priority", ["Low", "Medium", "High", "Critical"], required=True, default="Medium"))
        
        self.add_field(TextField("description", "Issue description", required=True, help_text="A clear and concise description of the issue."))
        
        self.add_field(MultiChoiceField("labels", "Issue labels", [
            "bug",
            "feature",
            "documentation",
            "question",
            "good first issue",
            "help wanted",
            "duplicate",
            "wontfix",
            "invalid",
        ], default=["bug"]))
        
        self.add_field(BooleanField("add_assignees", "Add assignees?", default=False))
    
    def render(self):
        """
        Render form.
        
        Returns:
            Dict[str, Any]: Form data
        """
        data = super().render()
        
        if data is None:
            return None
        
        # Add repository name if provided
        if hasattr(self, "repo_name"):
            data["repo_name"] = self.repo_name
        
        # Add assignees if requested
        if data.get("add_assignees"):
            assignees = []
            
            while True:
                # Get assignee username
                username = prompt("Assignee username")
                
                # Add assignee
                assignees.append(username)
                
                # Ask if user wants to add another assignee
                if not confirm("Add another assignee?", default=False):
                    break
            
            data["assignees"] = assignees
        else:
            data["assignees"] = []
        
        return data


def render_form(form):
    """
    Render a form.
    
    Args:
        form (Form): Form to render
        
    Returns:
        Dict[str, Any]: Form data
    """
    return form.render()


def create_repository_form():
    """
    Create a repository form.
    
    Returns:
        RepositoryForm: Repository form
    """
    return RepositoryForm()


def create_issue_form(repo_name=None):
    """
    Create an issue form.
    
    Args:
        repo_name (str, optional): Repository name. Defaults to None.
        
    Returns:
        IssueForm: Issue form
    """
    return IssueForm(repo_name)
