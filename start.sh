#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 &\nexport DISPLAY=:99\nexec gunicorn app:app
