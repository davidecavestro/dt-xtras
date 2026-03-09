#!/bin/bash

# DT Aggregator Environment Setup Script
# This script helps manage different environment configurations

set -e

echo "🔧 DT Aggregator Environment Setup"
echo "=================================="

# Function to show current environment
show_env() {
    echo "📋 Current Environment:"
    echo "  DT_API_URL: ${DT_API_URL:-not set}"
    echo "  DT_API_KEY: ${DT_API_KEY:+configured}"
    echo "  ENVIRONMENT: ${ENVIRONMENT:-not set}"
    echo ""
}

# Function to setup development environment
setup_dev() {
    echo "🛠️  Setting up Development Environment..."
    
    # Copy development environment
    if [ -f .env ]; then
        cp .env .env.backup
        echo "✅ Backed up existing .env to .env.backup"
    fi
    
    cp .env.dev .env
    echo "✅ Copied .env.dev to .env"
    echo "🔄 Restart devcontainer to apply changes"
    echo ""
    echo "Commands:"
    echo "  VS Code: Command Palette → 'Dev Containers: Rebuild Container'"
    echo "  Or: Stop and restart devcontainer manually"
}

# Function to setup production environment
setup_prod() {
    echo "🚀 Setting up Production Environment..."
    
    # Backup existing environment
    if [ -f .env ]; then
        cp .env .env.backup
        echo "✅ Backed up existing .env to .env.backup"
    fi
    
    cp .env.example .env
    echo "✅ Copied .env.example to .env"
    echo "⚠️  Please edit .env with your actual DT_API_KEY"
    echo "🐳 Then run: docker compose up -d"
    echo ""
}

# Function to start production containers
start_prod() {
    echo "🐳 Starting Production Containers..."
    
    if [ ! -f .env ]; then
        echo "❌ .env file not found. Please run './setup.sh prod' first"
        exit 1
    fi
    
    # Check if API key is set
    if grep -q "your-dt-api-key-here" .env; then
        echo "❌ Please set your actual DT_API_KEY in .env file"
        exit 1
    fi
    
    docker compose up -d
    echo "✅ Production containers started"
    echo "🌐 Frontend: http://localhost:${FRONTEND_PORT:-5173}"
    echo "🔧 Backend: http://localhost:${BACKEND_PORT:-8000}"
}

# Function to stop production containers
stop_prod() {
    echo "🛑 Stopping Production Containers..."
    docker compose down
    echo "✅ Containers stopped"
}

# Function to show help
show_help() {
    echo "📖 DT Aggregator Setup Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  show     - Show current environment variables"
    echo "  dev      - Setup development environment (devcontainer)"
    echo "  prod     - Setup production environment (docker compose)"
    echo "  start    - Start production containers"
    echo "  stop     - Stop production containers"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 show       # Show current setup"
    echo "  $0 dev        # Setup for development"
    echo "  $0 prod       # Setup for production"
    echo "  $0 start      # Start production"
    echo "  $0 stop       # Stop production"
}

# Main script logic
case "${1:-help}" in
    "show")
        show_env
        ;;
    "dev")
        setup_dev
        ;;
    "prod")
        setup_prod
        ;;
    "start")
        start_prod
        ;;
    "stop")
        stop_prod
        ;;
    "help"|*)
        show_help
        ;;
esac
