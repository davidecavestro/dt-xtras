#!/bin/bash

# Backend startup script
echo "🚀 Starting DT extras Backend..."
echo "📍 Directory: $(pwd)"
echo "🔧 Installing dependencies..."

cd backend
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo "🌟 Starting FastAPI server on http://0.0.0.0:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo "🌐 Access from host: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

export BACKEND_API_URL=http://0.0.0.0:8000
export DT_API_URL=http://dtrack-apiserver:8080
export DT_FRONTEND_URL=http://localhost:3000
python main.py
