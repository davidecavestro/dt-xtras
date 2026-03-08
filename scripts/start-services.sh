#!/bin/bash

# Main startup script - starts both backend and frontend
echo "🚀 Starting DT Aggregator Development Environment"
echo "=========================================="

# Create logs directory
mkdir -p logs

echo "📦 Starting backend..."
# Start backend in background with logging
./scripts/start-backend.sh > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting frontend..."
# Start frontend in background with logging  
./scripts/start-frontend.sh > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Services started!"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs" 
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "📋 Logs available in ./logs/"
echo "🛑 Stop services with: ./scripts/stop-services.sh"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for services
wait
