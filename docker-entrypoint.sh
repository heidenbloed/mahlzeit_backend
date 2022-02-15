#!/bin/bash

# Collect static files
echo "Collect static files"
python backend/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python backend/manage.py migrate

# Start server
echo "Starting server"
python backend/manage.py runserver 0.0.0.0:8000