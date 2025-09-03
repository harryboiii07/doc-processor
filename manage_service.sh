#!/bin/bash

# Django Excel to JSON Converter - Management Script
# This script provides easy commands for managing the service

set -e

PROJECT_NAME="excel-converter"
VENV_PATH="venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_info "Run: $0 setup"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    source "$VENV_PATH/bin/activate"
}

# Setup function
setup() {
    log_info "Setting up Django Excel to JSON Converter..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_PATH" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    activate_venv
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    log_info "Installing dependencies..."
    pip install -r requirements.txt
    
    # Create logs directory
    mkdir -p logs
    
    # Run migrations
    log_info "Running database migrations..."
    python manage.py migrate
    
    # Collect static files
    log_info "Collecting static files..."
    python manage.py collectstatic --noinput
    
    log_success "Setup completed successfully!"
    log_info "To start the development server, run: $0 dev"
    log_info "To run tests, run: $0 test"
}

# Development server
dev() {
    check_venv
    activate_venv
    
    log_info "Starting development server..."
    python manage.py runserver 0.0.0.0:8000
}

# Production server with gunicorn
prod() {
    check_venv
    activate_venv
    
    log_info "Starting production server with gunicorn..."
    gunicorn --bind 0.0.0.0:8000 \
             --workers 4 \
             --worker-class sync \
             --worker-connections 1000 \
             --max-requests 1000 \
             --max-requests-jitter 100 \
             --timeout 300 \
             --keep-alive 5 \
             --access-logfile - \
             --error-logfile - \
             excel_converter.wsgi:application
}

# Test function
test() {
    check_venv
    activate_venv
    
    log_info "Running service tests..."
    python test_service.py
}

# Docker functions
docker_build() {
    log_info "Building Docker image..."
    docker build -t $PROJECT_NAME .
    log_success "Docker image built successfully!"
}

docker_run() {
    log_info "Running Docker container..."
    docker run -p 8000:8000 \
               -v "$(pwd)/logs:/app/logs" \
               -e DEBUG=False \
               -e SECRET_KEY="docker-secret-key-change-in-production" \
               --name $PROJECT_NAME \
               $PROJECT_NAME
}

docker_compose_up() {
    log_info "Starting services with Docker Compose..."
    docker-compose up --build
}

docker_compose_down() {
    log_info "Stopping Docker Compose services..."
    docker-compose down
}

# Logs function
logs() {
    if [ -f "logs/excel_converter.log" ]; then
        log_info "Showing recent logs..."
        tail -f logs/excel_converter.log
    else
        log_warning "Log file not found. Make sure the service has been started."
    fi
}

# Health check
health() {
    log_info "Checking service health..."
    curl -s http://localhost:8000/health | python -m json.tool || log_error "Service not responding"
}

# Clean function
clean() {
    log_info "Cleaning up temporary files..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove test files
    rm -f test_*.xlsx test_*.xls perf_test_*.xlsx 2>/dev/null || true
    
    # Remove logs (optional)
    read -p "Remove log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f logs/*.log* 2>/dev/null || true
        log_info "Log files removed"
    fi
    
    log_success "Cleanup completed!"
}

# Show usage
usage() {
    echo "Django Excel to JSON Converter - Management Script"
    echo ""
    echo "Usage: $0 {setup|dev|prod|test|docker-build|docker-run|docker-up|docker-down|logs|health|clean}"
    echo ""
    echo "Commands:"
    echo "  setup        - Initial setup (create venv, install dependencies, migrate)"
    echo "  dev          - Start development server"
    echo "  prod         - Start production server with gunicorn"
    echo "  test         - Run service tests"
    echo "  docker-build - Build Docker image"
    echo "  docker-run   - Run Docker container"
    echo "  docker-up    - Start with Docker Compose"
    echo "  docker-down  - Stop Docker Compose"
    echo "  logs         - Show recent logs"
    echo "  health       - Check service health"
    echo "  clean        - Clean temporary files"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # First-time setup"
    echo "  $0 dev       # Start development server"
    echo "  $0 test      # Run tests"
}

# Main script logic
case "$1" in
    setup)
        setup
        ;;
    dev)
        dev
        ;;
    prod)
        prod
        ;;
    test)
        test
        ;;
    docker-build)
        docker_build
        ;;
    docker-run)
        docker_run
        ;;
    docker-up)
        docker_compose_up
        ;;
    docker-down)
        docker_compose_down
        ;;
    logs)
        logs
        ;;
    health)
        health
        ;;
    clean)
        clean
        ;;
    *)
        usage
        exit 1
        ;;
esac
