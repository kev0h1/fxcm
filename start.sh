#!/bin/bash

# Initialize a counter at 0
count=0

# Try to start Nginx up to 3 times
while [ $count -lt 3 ]; do
    nginx

    # Check if Nginx has started successfully
    if [ $? -eq 0 ]; then
        echo "Nginx started successfully"
        break
    else
        count=$((count+1))
        echo "Failed to start Nginx, retrying in 5 seconds ($count/3)"
        sleep 5
    fi
done

# If Nginx failed to start after 3 attempts, exit with an error
if [ $count -eq 3 ]; then
    echo "Failed to start Nginx after 3 attempts, exiting"
    exit 1
fi

# Start the FastAPI application
exec python -m uvicorn src.entry_points.app:create_app --host 0.0.0.0 --port 8000
