# Project Setup Scripts

This directory contains scripts for setting up basic Python and JavaScript projects. These scripts create the folder structure and necessary files for simple projects, including version management and dependency management.

## Python Project Setup

The `proj_setup_python.cmd` script creates a basic Python project with the following features:

- Project structure with source, tests, and docs directories
- Virtual environment for Python version management
- setup.py for package installation
- requirements.txt and dev-requirements.txt for dependency management
- README.md with installation and usage instructions
- .gitignore for Python projects
- Sample module and test
- pyproject.toml with configuration for Black, isort, and mypy
- MIT License
- Activation script for the virtual environment

### Usage

```cmd
proj_setup_python.cmd project_name
```

### Project Structure

The script creates the following structure:

```
project_name/
├── project_name/
│   ├── __init__.py
│   └── sample.py
├── tests/
│   ├── __init__.py
│   └── test_sample.py
├── docs/
├── venv/
├── setup.py
├── requirements.txt
├── dev-requirements.txt
├── README.md
├── .gitignore
├── pyproject.toml
├── LICENSE
└── activate.cmd
```

### Getting Started

After creating the project:

1. Navigate to the project directory: `cd project_name`
2. Activate the virtual environment: `activate.cmd`
3. Install dependencies: `pip install -r requirements.txt`
4. Install the package in development mode: `pip install -e .`
5. Run tests: `pytest`

## JavaScript Project Setup

The `proj_setup_js.cmd` script creates a basic JavaScript project with the following features:

- Project structure with source, test, and docs directories
- package.json for Node.js package management
- ESLint for code linting
- Prettier for code formatting
- Jest for testing
- README.md with installation and usage instructions
- .gitignore for Node.js projects
- Sample module and test
- MIT License
- .nvmrc for Node.js version management

### Usage

```cmd
proj_setup_js.cmd project_name
```

### Project Structure

The script creates the following structure:

```
project_name/
├── src/
│   └── index.js
├── test/
│   └── index.test.js
├── docs/
├── package.json
├── .gitignore
├── README.md
├── .eslintrc.js
├── .prettierrc
├── jest.config.js
├── LICENSE
├── .npmrc
└── .nvmrc
```

### Getting Started

After creating the project:

1. Navigate to the project directory: `cd project_name`
2. Install dependencies: `npm install`
3. Run tests: `npm test`
4. Start the application: `npm start`

## Requirements

### For Python Projects

- Python 3.6 or higher
- pip (usually comes with Python)

### For JavaScript Projects

- Node.js
- npm (comes with Node.js)

## Customization

You can customize these scripts to fit your specific needs by modifying the templates for each file. For example, you might want to:

- Add more dependencies to requirements.txt or package.json
- Change the license
- Add more directories to the project structure
- Configure different linting rules

## License

These scripts are provided under the MIT License. Feel free to use and modify them as needed.
