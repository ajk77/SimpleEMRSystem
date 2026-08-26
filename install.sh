#!/bin/bash

set -euo pipefail

echo "Simple EMR System - Automated Installation"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo
    echo "Please install Python 3.10+ from https://python.org"
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "On macOS: brew install python3"
    echo "On CentOS/RHEL: sudo yum install python3 python3-pip"
    echo
    exit 1
fi

echo "Python found. Checking version..."
python3 --version

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Django 5.2 requires 3.10+
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: Python 3.10 or higher is required (Django 5.2)"
    echo "Current version: $PYTHON_VERSION"
    echo "On macOS: brew install python@3.12  # or python@3.13"
    exit 1
fi

echo
echo "Creating virtual environment..."
# Recreate if a leftover semr_env was built with an older Python (e.g. 3.9).
# `venv` without --clear reuses the existing interpreter.
python3 -m venv --clear semr_env

VENV_PY="$(pwd)/semr_env/bin/python"
echo "Virtualenv Python:"
"$VENV_PY" --version
if ! "$VENV_PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: semr_env is not Python 3.10+"
    echo "Delete the semr_env folder and rerun, using a 3.10+ python3."
    exit 1
fi

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source semr_env/bin/activate

echo "Upgrading pip..."
"$VENV_PY" -m pip install --upgrade pip

echo
echo "Installing dependencies..."
if ! "$VENV_PY" -m pip install -r requirements.txt; then
    echo "ERROR: Failed to install dependencies"
    echo "See the pip output above."
    exit 1
fi

echo
echo "Setting up database..."
"$VENV_PY" manage.py migrate

echo
echo "Loading resources into database..."
"$VENV_PY" manage.py load_resources

echo
read -p "Would you like to create an admin user? (y/n): " create_admin
if [[ $create_admin == "y" || $create_admin == "Y" ]]; then
    echo "Creating admin user..."
    "$VENV_PY" manage.py createsuperuser
fi

if [ ! -d "resources" ]; then
    echo "Creating resources directory..."
    mkdir -p resources
fi

chmod +x ./*.sh 2>/dev/null || true

echo
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo
echo "Starting Simple EMR System..."
echo "Open your browser to: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo
read -p "Press Enter to start the server..."
"$VENV_PY" manage.py runserver
