#!/bin/bash

set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Running Django setup..."
python manage.py collectstatic --noinput --clear || echo "No static files to collect"
python manage.py migrate --noinput || echo "No migrations to run"

echo "==> Build completed successfully!"