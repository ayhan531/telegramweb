#!/bin/bash

# Start the Python Telegram Bot in the background with auto-restart
echo "Initializing database..."
python3 init_db.py

echo "Starting Userbot Relay in background..."
(
  while true; do
    echo "--- Launching Relay at $(date) ---"
    python3 ../matriks_bridge/userbot_relay.py 2>&1
    echo "Relay stopped. Restarting in 10 seconds..."
    sleep 10
  done
) &

echo "Starting Telegram Bot in background loop..."
(
  while true; do
    echo "--- Launching Bot at $(date) ---"
    python3 main.py 2>&1
    echo "Bot crashed or stopped with exit code $?. Restarting in 5 seconds..."
    sleep 5
  done
) &

# Start the Node.js API server in the foreground
echo "Starting API Server on port $PORT..."
node api_server.js
