@echo off
setlocal enabledelayedexpansion

echo ===== Python Project Setup =====

REM Check if project name is provided
if "%~1"=="" (
    echo ERROR: Project name is required.
    echo Usage: proj_setup_python.cmd project_name
    exit /b 1
)

set PROJECT_NAME=%~1
set PROJECT_DIR=%CD%\%PROJECT_NAME%

REM Check if project directory already exists
if exist "%PROJECT_DIR%" (
    echo ERROR: Directory "%PROJECT_NAME%" already exists.
    echo Please choose a different project name or delete the existing directory.
    exit /b 1
)

echo Creating Python project: %PROJECT_NAME%

REM Create project directory structure
echo Creating directory structure...
mkdir "%PROJECT_DIR%"
mkdir "%PROJECT_DIR%\%PROJECT_NAME%"
mkdir "%PROJECT_DIR%\tests"
mkdir "%PROJECT_DIR%\docs"

REM Create virtual environment
echo Creating virtual environment...
python -m venv "%PROJECT_DIR%\venv"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python is installed and in your PATH.
    exit /b 1
)

REM Create setup.py
echo Creating setup.py...
(
echo from setuptools import setup, find_packages
echo.
echo setup(
echo     name="%PROJECT_NAME%",
echo     version="0.1.0",
echo     packages=find_packages(),
echo     install_requires=[
echo         # Add your dependencies here
echo     ],
echo     author="Your Name",
echo     author_email="your.email@example.com",
echo     description="A short description of the project",
echo     keywords="python, project",
echo     url="https://github.com/yourusername/%PROJECT_NAME%",
echo     classifiers=[
echo         "Development Status :: 3 - Alpha",
echo         "Intended Audience :: Developers",
echo         "Programming Language :: Python :: 3",
echo         "Programming Language :: Python :: 3.6",
echo         "Programming Language :: Python :: 3.7",
echo         "Programming Language :: Python :: 3.8",
echo         "Programming Language :: Python :: 3.9",
echo     ],
echo     python_requires=">=3.6",
echo )
) > "%PROJECT_DIR%\setup.py"

REM Create requirements.txt
echo Creating requirements.txt...
(
echo # Add your dependencies here
echo pytest==7.3.1
echo pytest-cov==4.1.0
) > "%PROJECT_DIR%\requirements.txt"

REM Create dev-requirements.txt
echo Creating dev-requirements.txt...
(
echo # Development dependencies
echo pytest==7.3.1
echo pytest-cov==4.1.0
echo flake8==6.0.0
echo black==23.3.0
echo isort==5.12.0
echo mypy==1.3.0
) > "%PROJECT_DIR%\dev-requirements.txt"

REM Create README.md
echo Creating README.md...
(
echo # %PROJECT_NAME%
echo.
echo A short description of the project.
echo.
echo ## Installation
echo.
echo ```bash
echo # Clone the repository
echo git clone https://github.com/yourusername/%PROJECT_NAME%.git
echo cd %PROJECT_NAME%
echo.
echo # Create and activate virtual environment
echo python -m venv venv
echo venv\Scripts\activate  # On Windows
echo # source venv/bin/activate  # On Unix/macOS
echo.
echo # Install dependencies
echo pip install -r requirements.txt
echo.
echo # Install in development mode
echo pip install -e .
echo ```
echo.
echo ## Usage
echo.
echo ```python
echo import %PROJECT_NAME%
echo.
echo # Add usage examples here
echo ```
echo.
echo ## Development
echo.
echo ```bash
echo # Install development dependencies
echo pip install -r dev-requirements.txt
echo.
echo # Run tests
echo pytest
echo.
echo # Run tests with coverage
echo pytest --cov=%PROJECT_NAME%
echo ```
echo.
echo ## License
echo.
echo [MIT](LICENSE)
) > "%PROJECT_DIR%\README.md"

REM Create .gitignore
echo Creating .gitignore...
(
echo # Byte-compiled / optimized / DLL files
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo.
echo # C extensions
echo *.so
echo.
echo # Distribution / packaging
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo MANIFEST
echo.
echo # PyInstaller
echo #  Usually these files are written by a python PyInstaller build script
echo *.manifest
echo *.spec
echo.
echo # Installer logs
echo pip-log.txt
echo pip-delete-this-directory.txt
echo.
echo # Unit test / coverage reports
echo htmlcov/
echo .tox/
echo .nox/
echo .coverage
echo .coverage.*
echo .cache
echo nosetests.xml
echo coverage.xml
echo *.cover
echo *.py,cover
echo .hypothesis/
echo .pytest_cache/
echo.
echo # Environments
echo .env
echo .venv
echo env/
echo venv/
echo ENV/
echo env.bak/
echo venv.bak/
echo.
echo # IDE files
echo .idea/
echo .vscode/
echo *.swp
echo *.swo
) > "%PROJECT_DIR%\.gitignore"

REM Create __init__.py in the project package
echo Creating __init__.py...
(
echo """
echo %PROJECT_NAME% package.
echo """
echo.
echo __version__ = "0.1.0"
) > "%PROJECT_DIR%\%PROJECT_NAME%\__init__.py"

REM Create a sample module
echo Creating sample module...
(
echo """
echo Sample module.
echo """
echo.
echo def hello^(name: str^) -^> str:
echo     """
echo     Return a greeting message.
echo.
echo     Args:
echo         name: The name to greet.
echo.
echo     Returns:
echo         A greeting message.
echo     """
echo     return f"Hello, {name}!"
echo.
echo.
echo if __name__ == "__main__":
echo     print^(hello^("World"^)^)
) > "%PROJECT_DIR%\%PROJECT_NAME%\sample.py"

REM Create a sample test
echo Creating sample test...
(
echo """
echo Tests for the sample module.
echo """
echo.
echo import pytest
echo.
echo from %PROJECT_NAME%.sample import hello
echo.
echo.
echo def test_hello^(^):
echo     """Test the hello function."""
echo     assert hello^("World"^) == "Hello, World!"
echo     assert hello^("Python"^) == "Hello, Python!"
) > "%PROJECT_DIR%\tests\test_sample.py"

REM Create test __init__.py
echo Creating tests/__init__.py...
(
echo """
echo Test package.
echo """
) > "%PROJECT_DIR%\tests\__init__.py"

REM Create pyproject.toml
echo Creating pyproject.toml...
(
echo [build-system]
echo requires = ["setuptools>=42", "wheel"]
echo build-backend = "setuptools.build_meta"
echo.
echo [tool.black]
echo line-length = 88
echo target-version = ['py36', 'py37', 'py38', 'py39']
echo include = '\.pyi?$'
echo.
echo [tool.isort]
echo profile = "black"
echo line_length = 88
echo.
echo [tool.mypy]
echo python_version = "3.6"
echo warn_return_any = true
echo warn_unused_configs = true
echo disallow_untyped_defs = true
echo disallow_incomplete_defs = true
) > "%PROJECT_DIR%\pyproject.toml"

REM Create LICENSE file
echo Creating LICENSE file...
(
echo MIT License
echo.
echo Copyright ^(c^) 2023 Your Name
echo.
echo Permission is hereby granted, free of charge, to any person obtaining a copy
echo of this software and associated documentation files ^(the "Software"^), to deal
echo in the Software without restriction, including without limitation the rights
echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
echo copies of the Software, and to permit persons to whom the Software is
echo furnished to do so, subject to the following conditions:
echo.
echo The above copyright notice and this permission notice shall be included in all
echo copies or substantial portions of the Software.
echo.
echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
echo SOFTWARE.
) > "%PROJECT_DIR%\LICENSE"

REM Create a batch file to activate the virtual environment
echo Creating activate.cmd...
(
echo @echo off
echo call venv\Scripts\activate
) > "%PROJECT_DIR%\activate.cmd"

echo.
echo Python project "%PROJECT_NAME%" created successfully!
echo.
echo To get started:
echo   1. cd %PROJECT_NAME%
echo   2. activate.cmd
echo   3. pip install -r requirements.txt
echo   4. pip install -e .
echo   5. pytest
echo.
echo Happy coding!

endlocal
