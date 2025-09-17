@echo off
echo Simple EMR System - Automated Installation
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv semr_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call semr_env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run migrations
echo.
echo Setting up database...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to set up database
    pause
    exit /b 1
)

REM Create superuser (optional)
echo.
echo Would you like to create an admin user? (y/n)
set /p create_admin=
if /i "%create_admin%"=="y" (
    echo Creating admin user...
    python manage.py createsuperuser
)

REM Create resources directory if it doesn't exist
if not exist "resources" (
    echo Creating resources directory...
    mkdir resources
)

REM Start server
echo.
echo ==========================================
echo Installation complete!
echo ==========================================
echo.
echo Starting Simple EMR System...
echo Open your browser to: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
pause
python manage.py runserver
