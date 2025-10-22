#!/bin/bash
# Startup script for Railway deployment

# Get port from environment or default to 8000
PORT=${PORT:-8000}

# Run with multiple workers if sufficient memory, otherwise single worker
if [ "${RAILWAY_ENVIRONMENT}" = "production" ]; then
    echo "Starting with 2 workers for production..."
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
else
    echo "Starting with 1 worker for development..."
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
fi