#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting setup for Karoseri Component Damage Classification..."

# 1. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# 2. Activate Virtual Environment
echo "Activating virtual environment..."
source .venv/bin/activate

# 3. Install/Upgrade Dependencies
echo "Upgrading pip..."
pip3 install --upgrade pip

echo "Installing dependencies from requirements.txt..."
pip3 install -r requirements.txt

echo "✅ Setup completed successfully!"
echo "You can now run the application using ./run.sh"
