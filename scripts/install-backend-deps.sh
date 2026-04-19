#!/bin/bash

# Backend deps install script
echo "📍 Directory: $(pwd)"
echo "🔧 Installing dependencies..."

cd backend
pip install -r requirements.txt

echo "✅ Dependencies installed"
