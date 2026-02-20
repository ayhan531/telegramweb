#!/bin/bash

# Start the Node.js API server in the background
# Use the PORT environment variable provided by Render
echo "Starting API Server on port $PORT..."
node api_server.js &

# Wait a moment for the server to initialize
sleep 2

# Start the Python Telegram Bot
echo "Starting Telegram Bot..."
python3 main.py
