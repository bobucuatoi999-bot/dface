#!/bin/bash

echo "========================================"
echo "  FaceStream - Starting Backend & Frontend"
echo "========================================"
echo ""

echo "[1/3] Starting Backend Server..."
cd backend
python -m app.main &
BACKEND_PID=$!
cd ..
sleep 3

echo "[2/3] Installing Frontend Dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
else
    echo "Dependencies already installed."
fi

echo "[3/3] Starting Frontend..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

