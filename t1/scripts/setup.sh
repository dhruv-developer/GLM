#!/bin/bash

echo "🚀 Setting up ZIEL-MAS..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Update .env with your configuration"
echo "2. Start Redis: redis-server"
echo "3. Start MongoDB: mongod"
echo "4. Run backend: python backend/main.py"
echo "5. Run frontend: cd frontend && npm run dev"
echo ""
echo "🎯 ZIEL-MAS will be available at:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
