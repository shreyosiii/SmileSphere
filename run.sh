#!/bin/bash

# SmileSphere Application Runner

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies if not already installed
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

# Initialize database if it doesn't exist
if [ ! -f "instance/smilesphere.db" ]; then
    echo "Initializing database with sample data..."
    python init_db.py --with-sample-data
    if [ $? -ne 0 ]; then
        echo "Error: Failed to initialize database."
        exit 1
    fi
fi

# Run the application
echo "Starting SmileSphere application..."
echo "Open your browser and navigate to http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
python app.py