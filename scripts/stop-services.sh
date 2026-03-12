#!/bin/bash

echo "🛑 Stopping DT extras Services"

# Stop DT services
echo "🐳 Stopping DT services..."
cd .devcontainer && docker compose down
cd ..

# Kill any running Python backend processes
echo "🔧 Stopping backend..."
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Backend stopped" || echo "ℹ️ Backend not running"

# Kill any running Vite frontend processes
echo "🎨 Stopping frontend..."
pkill -f "vite" 2>/dev/null && echo "✅ Frontend stopped" || echo "ℹ️ Frontend not running"

# Kill any remaining node processes on port 5173
echo "🧹 Cleaning up port 5173..."
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "✅ Port 5173 cleared" || echo "ℹ️ Port 5173 already clear"

# Kill any remaining python processes on port 8000
echo "🧹 Cleaning up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Port 8000 cleared" || echo "ℹ️ Port 8000 already clear"

echo "✅ All services stopped"
