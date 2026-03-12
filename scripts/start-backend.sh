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

python main.py
