#!/bin/bash
set -e # Exit on error

echo "--- BUILDING PROJECT ---"

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
playwright install chromium

# 2. Build Frontend
echo "Building Frontend (web-app)..."
cd web-app
npm install
npm run build
cd ..

# 3. Install Backend dependencies
echo "Installing Backend dependencies (src)..."
cd src
npm install
cd ..

echo "--- BUILD COMPLETE ---"
