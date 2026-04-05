#!/bin/bash

# ZIEL-MAS Development Startup Script

echo "🚀 Starting ZIEL-MAS Development Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if required services are running
check_service() {
    if pgrep -x "$1" > /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is running"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not running"
        return 1
    fi
}

# Function to start services
start_services() {
    echo "Starting required services..."

    # Start MongoDB if not running
    if ! check_service "mongod"; then
        echo "Starting MongoDB..."
        brew services start mongodb-community 2>/dev/null || mongod --fork --logpath /tmp/mongodb.log
        sleep 2
    fi

    # Start Redis if not running
    if ! check_service "redis-server"; then
        echo "Starting Redis..."
        brew services start redis 2>/dev/null || redis-server --daemonize yes
        sleep 2
    fi
}

# Check dependencies
check_dependencies() {
    echo "Checking dependencies..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
    else
        echo -e "${RED}✗${NC} Python 3 is required but not installed"
        exit 1
    fi

    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
    else
        echo -e "${RED}✗${NC} Node.js is required but not installed"
        exit 1
    fi

    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓${NC} npm found: $NPM_VERSION"
    else
        echo -e "${RED}✗${NC} npm is required but not installed"
        exit 1
    fi
}

# Check backend environment
check_backend_env() {
    if [ ! -f "backend/.env" ]; then
        echo -e "${YELLOW}⚠${NC} Backend .env file not found"
        echo "Creating from .env.example..."
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo -e "${YELLOW}⚠${NC} Please edit backend/.env and add your GLM API key"
            echo ""
            read -p "Press Enter to continue after updating .env..."
        else
            echo -e "${RED}✗${NC} backend/.env.example not found"
            exit 1
        fi
    fi
}

# Install backend dependencies
install_backend() {
    if [ ! -d "backend/venv" ]; then
        echo "Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
    fi

    echo "Installing backend dependencies..."
    cd backend
    source venv/bin/activate
    pip install -q -r requirements.txt
    cd ..
}

# Install frontend dependencies
install_frontend() {
    if [ ! -d "frontend/node_modules" ]; then
        echo "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
}

# Start backend
start_backend() {
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    echo -e "${GREEN}✓${NC} Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
}

# Start frontend
start_frontend() {
    echo "Starting frontend server..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    echo -e "${GREEN}✓${NC} Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
}

# Main execution
main() {
    # Check dependencies
    check_dependencies

    # Start services
    start_services
    echo ""

    # Check environment
    check_backend_env
    echo ""

    # Install dependencies
    install_backend
    install_frontend
    echo ""

    # Start servers
    start_backend
    sleep 3
    start_frontend
    echo ""

    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ZIEL-MAS is now running!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Logs:"
    echo "  Backend:  tail -f backend.log"
    echo "  Frontend: tail -f frontend.log"
    echo ""
    echo "To stop all servers, run: ./stop.sh or kill $(cat backend.pid) $(cat frontend.pid)"
    echo ""
}

# Run main function
main