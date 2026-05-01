#!/bin/bash

# Backend startup script
echo "🚀 Starting DT extras Backend..."
echo "📍 Directory: $(pwd)"
echo "🔧 Installing dependencies..."

cd backend
pip install -r requirements.txt

export BACKEND_API_URL=http://0.0.0.0:8000
export DT_API_URL=http://dtrack-apiserver:8080
export DT_FRONTEND_URL=http://localhost:3000
export CORS_ORIGINS=http://localhost:5173,http://localhost:8080,http://localhost:3000,http://localhost:3001

echo "✅ Dependencies installed"
echo "🌟 Starting FastAPI server on $BACKEND_API_URL"
echo "📖 API docs available at $BACKEND_API_URL/docs"
echo "🌐 Access from host: $BACKEND_API_URL"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
