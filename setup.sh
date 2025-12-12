#!/bin/bash

# Dashboard Keuangan - Quick Setup Script
# Run this script untuk quick setup semua dependencies

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Dashboard Keuangan Perbankan - kwd-dashboard Setup           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check Node.js
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16 or higher"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION found"
echo ""

# Install Python dependencies
echo "📥 Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip install flask pandas openpyxl
echo "✅ Python dependencies installed"
echo ""

# Install Node dependencies
echo "📥 Installing Node.js dependencies..."
cd kwd-dashboard
npm install
cd ..
echo "✅ Node.js dependencies installed"
echo ""

# Check data file
echo "📁 Checking data file..."
if [ -f "data/KINERJA PERBANKAN.xlsx" ]; then
    echo "✅ Data file found: data/KINERJA PERBANKAN.xlsx"
else
    echo "⚠️  Data file not found at: data/KINERJA PERBANKAN.xlsx"
    echo "    Please make sure the Excel file is placed in the data/ folder"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   ✨ Setup Complete!                                          ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  To start development:                                         ║"
echo "║                                                                ║"
echo "║  Terminal 1 (Frontend - Vite):                                 ║"
echo "║  $ cd kwd-dashboard && npm run dev                             ║"
echo "║  Open: http://localhost:5173                                   ║"
echo "║                                                                ║"
echo "║  Terminal 2 (Backend - Flask):                                 ║"
echo "║  $ python3 server.py                                           ║"
echo "║  Open: http://localhost:5000/keuangan                          ║"
echo "║                                                                ║"
echo "║  API Documentation:                                            ║"
echo "║  GET /api/data - Returns dashboard data                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
