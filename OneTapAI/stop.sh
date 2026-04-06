#!/bin/bash

# ZIEL-MAS Stop Script

echo "🛑 Stopping ZIEL-MAS Development Environment..."
echo ""

# Kill processes by PID files
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "Stopped backend server (PID: $BACKEND_PID)"
    fi
    rm backend.pid
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "Stopped frontend server (PID: $FRONTEND_PID)"
    fi
    rm frontend.pid
fi

# Also try to kill by port (fallback)
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "Stopped backend on port 8000"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "Stopped frontend on port 3000"

echo ""
echo "All servers stopped."