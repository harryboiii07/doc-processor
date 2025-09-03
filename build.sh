#!/usr/bin/env bash
# build.sh - Render build script for Excel Converter API

set -o errexit  # Exit on error

echo "🚀 Starting build process for Excel Converter API..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y \
    libmagic1 \
    libmagic-dev \
    file \
    --no-install-recommends

# Clean up apt cache to reduce image size
rm -rf /var/lib/apt/lists/*

echo "🐍 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

echo "🔧 Running Django setup..."

# Collect static files (if you add static files later)
python manage.py collectstatic --noinput --clear || echo "No static files to collect"

# Run database migrations (if you add a database later)
python manage.py migrate --noinput || echo "No migrations to run"

# Create media directory for temporary files
mkdir -p media/temp

echo "✅ Build completed successfully!"
echo "🎯 Service will be available at the provided Render URL"
