#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 &

# Export display environment variable
export DISPLAY=:99

# Start the Flask app using Gunicorn
exec gunicorn app:app
