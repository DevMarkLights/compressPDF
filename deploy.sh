#!/bin/bash

echo "Starting deployment process..."

# Check if we are in the right directory
if [ ! -f "runApp.bash" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to install frontend dependencies"
    exit 1
fi

# Build frontend
echo "Building frontend..."
python3 build.py
if [ $? -ne 0 ]; then
    echo "Frontend build failed"
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd ../backend

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Ghostscript is installed
echo "Checking Ghostscript installation..."
if ! command -v gs &> /dev/null; then
    echo "Ghostscript not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ghostscript
    elif command -v yum &> /dev/null; then
        sudo yum install -y ghostscript
    elif command -v brew &> /dev/null; then
        brew install ghostscript
    else
        echo "Please install Ghostscript manually"
        exit 1
    fi
fi

echo "Deployment setup complete!"
echo "Starting application..."

# Start the application
python -m uvicorn main:app --host 0.0.0.0 --port 8084 --workers 1