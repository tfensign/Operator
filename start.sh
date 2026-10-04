#!/bin/bash

echo "Starting Operator Web App..."
echo ""

# Check if backend port is in use
if lsof -i :3001 > /dev/null 2>&1; then
  echo "⚠️  Port 3001 already in use. Killing existing process..."
  kill $(lsof -t -i:3001) 2>/dev/null
  sleep 1
fi

# Check if frontend port is in use
if lsof -i :3000 > /dev/null 2>&1; then
  echo "⚠️  Port 3000 already in use. Killing existing process..."
  kill $(lsof -t -i:3000) 2>/dev/null
  sleep 1
fi

echo "Starting Backend (port 3001)..."
cd backend
python -m uvicorn app:app --port 3001 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
echo "  Logs: backend.log"
echo ""

# Wait for backend to start
sleep 2

echo "Starting Frontend (port 3000)..."
cd ../frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"
echo "  Logs: frontend.log"
echo ""

echo "=========================================="
echo "✅ Operator is starting!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:3001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Open http://localhost:3000 in your browser"
echo ""
echo "To stop: Ctrl+C or run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Check logs:"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"
echo "=========================================="
echo ""

# Keep script running
wait
