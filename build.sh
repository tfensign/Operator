#!/bin/bash
set -e

echo "🔨 Building Operator..."

# Install Python backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies and build
echo "Installing frontend dependencies..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
