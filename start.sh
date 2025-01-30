#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 &

# Export display environment variable
export DISPLAY=:99

# Ensure the .Xauthority file is in place
xauth generate :99 . trusted
xauth add $(xauth list)
chmod 600 ./.Xauthority

# Start the Flask app using Gunicorn
exec gunicorn app:app
