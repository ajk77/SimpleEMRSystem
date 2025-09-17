#!/bin/bash

echo "Simple EMR System - Automated Installation"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo
    echo "Please install Python 3.8+ from https://python.org"
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "On macOS: brew install python3"
    echo "On CentOS/RHEL: sudo yum install python3 python3-pip"
    echo
    exit 1
fi

echo "Python found. Checking version..."
python3 --version

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Check if version is 3.8 or higher
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "ERROR: Python 3.8 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv semr_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source semr_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Run migrations
echo
echo "Setting up database..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to set up database"
    exit 1
fi

# Create superuser (optional)
echo
read -p "Would you like to create an admin user? (y/n): " create_admin
if [[ $create_admin == "y" || $create_admin == "Y" ]]; then
    echo "Creating admin user..."
    python manage.py createsuperuser
fi

# Create resources directory if it doesn't exist
if [ ! -d "resources" ]; then
    echo "Creating resources directory..."
    mkdir -p resources
fi

# Make scripts executable
chmod +x *.sh

# Start server
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
python manage.py runserver
