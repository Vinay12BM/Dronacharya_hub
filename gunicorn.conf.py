import os

# Port settings for Render
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Gunicorn setup
timeout = 120
workers = 1 
preload_app = True
