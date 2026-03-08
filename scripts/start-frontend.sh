#!/bin/bash

# Frontend startup script
echo "🚀 Starting DT Aggregator Frontend..."
echo "📍 Directory: $(pwd)"
echo "🔧 Installing dependencies..."

cd frontend
npm install

echo "✅ Dependencies installed"
echo "🌟 Starting Vite dev server on http://localhost:5173"
echo "🌐 Access from host: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
