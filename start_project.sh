#!/bin/bash

echo "🚀 Starting Invoice QC Service..."

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start backend
echo "📡 Starting Backend API..."
nohup uvicorn invoice_qc.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Test backend
echo "🧪 Testing Backend..."
curl -s http://localhost:8000/health

# Open frontend in Chrome
echo "🌐 Opening Frontend..."
open -a "Google Chrome" frontend/index.html

# Open Swagger UI
echo "📚 Opening API Documentation..."
open -a "Google Chrome" http://localhost:8000/docs

echo ""
echo "✅ Invoice QC Service is running!"
echo ""
echo "📍 Access Points:"
echo "   - Frontend: frontend/index.html (opened in Chrome)"
echo "   - API: http://localhost:8000"
echo "   - Swagger UI: http://localhost:8000/docs (opened in Chrome)"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "🛑 To stop: lsof -ti:8000 | xargs kill -9"
