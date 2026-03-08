#!/bin/bash

# Backend startup script
echo "🚀 Starting DT Aggregator Backend..."
echo "📍 Directory: $(pwd)"
echo "🔧 Installing dependencies..."

cd backend
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
