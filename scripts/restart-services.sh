#!/bin/bash

echo "🔄 Restarting DT Aggregator Services"
echo "=================================="

# Stop all services first
echo "🛑 Stopping existing services..."
./scripts/stop-services.sh

# Wait a moment for cleanup
sleep 2

echo ""
echo "🚀 Starting DT Aggregator Development Environment"
echo "=========================================="

# Create logs directory
mkdir -p logs

echo "🐳 Starting DT services..."
# Start DT services from docker-compose
cd .devcontainer && docker compose up -d dtrack-db dtrack-apiserver dtrack-frontend
cd ..

# Wait for DT services to be ready
echo "⏳ Waiting for DT API to be ready..."
for i in {1..30}; do
    if curl -s http://dtrack-apiserver:8080/v1/user/login > /dev/null; then
        echo "✅ DT API is ready!"
        break
    fi
    echo "⏳ Waiting for DT API... ($i/30)"
    sleep 2
done

echo "📦 Starting backend..."
# Start backend in background with logging
cd backend && nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Check if backend is still running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
fi

echo "🎨 Starting frontend..."
# Start frontend in background with logging
cd frontend && nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait a moment for frontend to start
sleep 5

# Check if frontend is still running
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend started successfully"
else
    echo "❌ Frontend failed to start - trying alternative method"
    # Try alternative approach - run in background with explicit shell
    cd frontend && (npm run dev > ../logs/frontend.log 2>&1 &) && sleep 2
    FRONTEND_PID=$(pgrep -f "npm.*dev" | head -1)
    if [ -n "$FRONTEND_PID" ]; then
        echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend failed to start"
    fi
fi

echo ""
echo "✅ Services restarted!"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:5173"
echo "🐳 DT Frontend: http://localhost:3000"
echo ""
echo "📋 Logs available in ./logs/"
echo "🛑 Stop services with: ./scripts/stop-services.sh"
echo ""

# Don't wait - exit immediately after starting services
