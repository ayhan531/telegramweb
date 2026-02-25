#!/bin/bash

# Start the Python Telegram Bot in the background with auto-restart
# This handles the Conflict error during Render's Zero-Downtime deployment
echo "Initializing database..."
python3 init_db.py

echo "Starting Telegram Bot in background loop..."
(
  while true; do
    python3 main.py
    echo "Bot crashed or stopped (likely Conflict with old instance). Restarting in 5 seconds..."
    sleep 5
  done
) &

# Start the Node.js API server in the foreground
# This allows Render to detect the open port and mark the deploy as healthy
echo "Starting API Server on port $PORT..."
node api_server.js
