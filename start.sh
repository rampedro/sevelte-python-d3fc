#!/bin/bash

# Startup script for Svelte Python D3FC Dashboard

echo "🚀 Starting Svelte Python D3FC Dashboard..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find an available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while [ $port -le 65535 ]; do
        if ! lsof -i :$port >/dev/null 2>&1; then
            echo $port
            return
        fi
        port=$((port + 1))
    done
    
    echo "No available port found starting from $start_port" >&2
    exit 1
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🔄 Killing processes on port $port..."
        echo $pids | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    kill_port $BACKEND_PORT 2>/dev/null
    kill_port $FRONTEND_PORT 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check prerequisites
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "📁 Project directory: $SCRIPT_DIR"

# Find available ports
BACKEND_PORT=$(find_available_port 8000)
FRONTEND_PORT=$(find_available_port 5173)

echo "🔍 Found available ports:"
echo "   Backend: $BACKEND_PORT"
echo "   Frontend: $FRONTEND_PORT"

# Kill any existing processes on these ports (just in case)
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT

# Start backend
echo "🐍 Starting Python backend..."
cd "$SCRIPT_DIR/backend"

# Check if we're in a virtual environment, if not try to activate one
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo "📦 Activating virtual environment..."
        source venv/bin/activate
    elif [ -d "../asd" ]; then
        echo "📦 Activating virtual environment..."
        source ../asd/bin/activate
    fi
fi

# Install FastAPI and uvicorn if not already installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install fastapi uvicorn
fi

# Start backend in background
echo "🟢 Starting FastAPI server on http://localhost:$BACKEND_PORT"
uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:$BACKEND_PORT/ >/dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "❌ Backend failed to start"
        cleanup
        exit 1
    fi
done

# Update frontend configuration to use the dynamic backend port
cd "$SCRIPT_DIR/frontend"

# Create or update .env file with backend URL
echo "VITE_API_URL=http://localhost:$BACKEND_PORT" > .env

# Install dependencies if node_modules doesn't exist
if [ ! -d node_modules ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start frontend
echo "⚡ Starting Svelte frontend on http://localhost:$FRONTEND_PORT..."
echo ""
echo "🎉 Dashboard is ready!"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend API: http://localhost:$BACKEND_PORT"
echo ""
echo "Press Ctrl+C to stop all servers"

# Start frontend (this will block)
npm run dev -- --port $FRONTEND_PORT

# This line should not be reached unless frontend exits
cleanup