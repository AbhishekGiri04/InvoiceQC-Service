#!/bin/bash

# Setup script for Invoice QC Service
echo "=========================================="
echo "Invoice QC Service - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p extracted reports

# Run tests
echo ""
echo "Running tests..."
pytest tests/ -v

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run CLI: python -m invoice_qc.cli full-run --pdf-dir pdfs --report reports/result.json"
echo "3. Start API: uvicorn invoice_qc.api.main:app --reload"
echo "4. Open browser: http://localhost:8000/docs"
echo ""
