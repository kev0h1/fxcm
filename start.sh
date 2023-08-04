#!/bin/bash

# Start Nginx in the background
nginx &

# Start the FastAPI application
exec python -m uvicorn src.entry_points.app:create_app --host 0.0.0.0 --port 8000