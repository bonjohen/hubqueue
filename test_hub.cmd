@echo off

setlocal enabledelayedexpansion

echo ===== HubQueue Comprehensive Demo =====
echo This script demonstrates all the core functionality of HubQueue

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    exit /b 1
)

REM Create and activate virtual environment if it doesn't exist
if not exist venv_hubqueue (
    echo Creating virtual environment...
    python -m venv venv_hubqueue
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
)

echo Activating virtual environment...
call .\venv_hubqueue\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Install HubQueue if not already installed
pip show hubqueue >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing HubQueue...
    pip install -e .
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install HubQueue
        exit /b 1
    )
)

REM Check for GitHub token in system environment variables (silently)
if "%GITHUB_TOKEN%"=="" (
    echo WARNING: GITHUB_TOKEN environment variable is not set.
    echo Please set your GitHub token as an environment variable:
    echo set GITHUB_TOKEN=your_token_here
    echo.
    echo You can create a token at: https://github.com/settings/tokens
    echo Required scopes: repo, user, admin:org, delete_repo
    echo.
    set /p GITHUB_TOKEN=Enter your GitHub token (will not be saved): 
    if "!GITHUB_TOKEN!"=="" (
        echo No token provided. Some commands may fail.
    )
)

echo.
echo ===== Environment setup complete =====
echo.

REM Repository Management
echo ===== STEP 1: Repository Management =====
echo.

echo ===== STEP 1.1: Listing repositories =====
hubqueue repository list
echo.

echo ===== STEP 1.2: Creating a repository =====
hubqueue repository create test-hubqueue-demo "A test repository for HubQueue demo" --private
set CREATE_RESULT=%ERRORLEVEL%
if %CREATE_RESULT% neq 0 (
    echo WARNING: Failed to create repository 'test-hubqueue-demo'. This may be normal if the repository already exists.
) else (
    echo Repository 'test-hubqueue-demo' created successfully.
)
echo.

echo ===== STEP 1.3: Getting repository information =====
hubqueue repository get test-hubqueue-demo
echo.

echo ===== STEP 1.4: Updating repository description =====
hubqueue repository update test-hubqueue-demo --description "Updated description for HubQueue demo repository"
echo.

echo ===== STEP 1.5: Creating README file =====
hubqueue repository generate-readme test-hubqueue-demo "Test HubQueue Demo" "A test repository for demonstrating HubQueue functionality"
echo.

echo ===== STEP 1.6: Creating .gitignore file =====
hubqueue repository generate-gitignore test-hubqueue-demo Python
echo.

echo ===== STEP 1.7: Creating LICENSE file =====
hubqueue repository generate-license test-hubqueue-demo mit
echo.

REM Branch Operations
echo ===== STEP 2: Branch Operations =====
echo.

echo ===== STEP 2.1: Listing branches =====
hubqueue branch list test-hubqueue-demo
echo.

echo ===== STEP 2.2: Creating a branch =====
hubqueue branch create test-hubqueue-demo feature-branch
echo.

echo ===== STEP 2.3: Setting default branch =====
hubqueue branch set-default test-hubqueue-demo main
echo.

REM Issue Tracking
echo ===== STEP 3: Issue Tracking =====
echo.

echo ===== STEP 3.1: Creating issues =====
hubqueue issue create test-hubqueue-demo "Test Issue 1" "This is a test issue for HubQueue demo" --labels bug,documentation
echo.
hubqueue issue create test-hubqueue-demo "Test Issue 2" "This is another test issue for HubQueue demo" --labels enhancement,priority:high
echo.

echo ===== STEP 3.2: Listing issues =====
hubqueue issue list test-hubqueue-demo
echo.

echo ===== STEP 3.3: Getting issue details =====
REM Get the first issue number
for /f "tokens=1" %%i in ('hubqueue issue list test-hubqueue-demo ^| findstr "#"') do (
    set ISSUE_NUMBER=%%i
    set ISSUE_NUMBER=!ISSUE_NUMBER:#=!
    goto :found_issue
)
:found_issue
echo Getting details for issue #!ISSUE_NUMBER!
hubqueue issue get test-hubqueue-demo !ISSUE_NUMBER!
echo.

echo ===== STEP 3.4: Updating an issue =====
hubqueue issue update test-hubqueue-demo !ISSUE_NUMBER! --title "Updated Test Issue" --state closed
echo.

echo ===== STEP 3.5: Adding a comment to an issue =====
hubqueue issue comment test-hubqueue-demo !ISSUE_NUMBER! "This is a test comment from HubQueue demo"
echo.

REM Release Management
echo ===== STEP 4: Release Management =====
echo.

echo ===== STEP 4.1: Creating a release =====
hubqueue release create test-hubqueue-demo v1.0.0 "First Release" "This is the first release of HubQueue demo" --target main
echo.

echo ===== STEP 4.2: Listing releases =====
hubqueue release list test-hubqueue-demo
echo.

echo ===== STEP 4.3: Getting release details =====
hubqueue release get test-hubqueue-demo v1.0.0
echo.

REM Collaboration
echo ===== STEP 5: Collaboration =====
echo.

echo ===== STEP 5.1: Managing collaborators =====
echo NOTE: This step requires a valid GitHub username. Replace 'collaborator-username' with a real username.
echo Skipping actual collaborator addition to avoid errors.
echo Example command: hubqueue repository manage-collaborators test-hubqueue-demo collaborator-username add --permission read
echo.

REM Notifications
echo ===== STEP 6: Notifications =====
echo.

echo ===== STEP 6.1: Listing notifications =====
hubqueue notification list
echo.

REM Interactive Features
echo ===== STEP 7: Interactive Features =====
echo.

echo ===== STEP 7.1: UI Customization =====
hubqueue ui color --enable
echo.

echo ===== STEP 7.2: Error Handling =====
hubqueue error debug --enable
echo.
hubqueue error test --type input
echo.

REM Cleanup
echo ===== STEP 8: Cleanup =====
echo.

echo ===== STEP 8.1: Deleting the test repository =====
echo NOTE: This will delete the test repository 'test-hubqueue-demo'
set /p CONFIRM=Do you want to delete the test repository? (y/n): 
if /i "%CONFIRM%"=="y" (
    hubqueue repository delete test-hubqueue-demo --confirm
    echo Repository deleted.
) else (
    echo Repository deletion skipped.
)
echo.

echo ===== Demo completed successfully =====
echo.

echo This script demonstrated the following HubQueue operations:
echo 1. Repository Management
echo    - Listing repositories
echo    - Creating a repository
echo    - Getting repository information
echo    - Updating repository description
echo    - Creating README, .gitignore, and LICENSE files
echo 2. Branch Operations
echo    - Listing branches
echo    - Creating a branch
echo    - Setting default branch
echo 3. Issue Tracking
echo    - Creating issues
echo    - Listing issues
echo    - Getting issue details
echo    - Updating an issue
echo    - Adding a comment to an issue
echo 4. Release Management
echo    - Creating a release
echo    - Listing releases
echo    - Getting release details
echo 5. Collaboration
echo    - Managing collaborators (example only)
echo 6. Notifications
echo    - Listing notifications
echo 7. Interactive Features
echo    - UI Customization
echo    - Error Handling
echo 8. Cleanup
echo    - Deleting the test repository
echo.

echo For more details, see the documentation in the docs/ directory.

REM Deactivate virtual environment
call deactivate

endlocal
