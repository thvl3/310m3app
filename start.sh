#!/bin/bash

# Activate virtual environment
. .venv/bin/activate

# Handle Ctrl+C to terminate both processes
trap 'kill $(jobs -p); exit' INT

# Start the servers in the background
python -m http.server 8000 &
python restaurant_quiz_backend.py &

echo "Running at http://0.0.0.0:8000/"

# Wait for processes to finish
wait

