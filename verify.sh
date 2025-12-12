#!/bin/bash
# Dashboard Keuangan Integration - Verification Checklist

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Dashboard Keuangan Integration - Verification Checklist    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

ROOT_DIR="/Users/960072/Downloads/dashboard_keuangan 3"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2 (missing: $1)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2 (missing: $1)"
        return 1
    fi
}

echo "📁 DIRECTORY STRUCTURE"
echo "────────────────────────────────────────────────────────────────"
check_dir "$ROOT_DIR" "Root directory"
check_dir "$ROOT_DIR/kwd-dashboard" "kwd-dashboard folder"
check_dir "$ROOT_DIR/data" "data folder"
check_dir "$ROOT_DIR/kwd-dashboard/src/html" "HTML templates"
check_dir "$ROOT_DIR/kwd-dashboard/src/data" "Data definitions"
echo ""

echo "🐍 BACKEND FILES"
echo "────────────────────────────────────────────────────────────────"
check_file "$ROOT_DIR/server.py" "server.py (Flask API)"
check_file "$ROOT_DIR/requirements.txt" "requirements.txt (Python deps)"
check_file "$ROOT_DIR/app.py" "app.py (Legacy - optional)"
echo ""

echo "🎨 FRONTEND FILES"
echo "────────────────────────────────────────────────────────────────"
check_file "$ROOT_DIR/kwd-dashboard/src/html/keuangan.html" "keuangan.html (Dashboard template)"
check_file "$ROOT_DIR/kwd-dashboard/src/data/pages/keuangan.js" "keuangan.js (Data structure)"
check_file "$ROOT_DIR/index.html" "index.html (Landing page)"
check_file "$ROOT_DIR/kwd-dashboard/src/data/navigationLinks.js" "navigationLinks.js (Updated)"
echo ""

echo "📚 DOCUMENTATION"
echo "────────────────────────────────────────────────────────────────"
check_file "$ROOT_DIR/START_HERE.md" "START_HERE.md (Quick start - BAHASA INDONESIA!)"
check_file "$ROOT_DIR/SETUP.md" "SETUP.md (Detailed setup)"
check_file "$ROOT_DIR/README.md" "README.md (Project overview)"
check_file "$ROOT_DIR/INTEGRATION_SUMMARY.md" "INTEGRATION_SUMMARY.md (Technical details)"
echo ""

echo "🚀 SETUP SCRIPTS"
echo "────────────────────────────────────────────────────────────────"
check_file "$ROOT_DIR/setup.sh" "setup.sh (macOS/Linux setup)"
check_file "$ROOT_DIR/setup.bat" "setup.bat (Windows setup)"
check_file "$ROOT_DIR/.gitignore" ".gitignore (Git configuration)"
echo ""

echo "📊 DATA FILES"
echo "────────────────────────────────────────────────────────────────"
if [ -f "$ROOT_DIR/data/KINERJA PERBANKAN.xlsx" ]; then
    echo -e "${GREEN}✅${NC} KINERJA PERBANKAN.xlsx (Data file)"
else
    echo -e "${YELLOW}⚠️${NC}  KINERJA PERBANKAN.xlsx (Data file not found)"
    echo "    Please ensure Excel file is in data/ folder"
fi
echo ""

echo "🔧 DEPENDENCIES CHECK"
echo "────────────────────────────────────────────────────────────────"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅${NC} Python: $PYTHON_VERSION"
else
    echo -e "${RED}❌${NC} Python not found (required: Python 3.8+)"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅${NC} Node.js: $NODE_VERSION"
else
    echo -e "${RED}❌${NC} Node.js not found (required: Node 16+)"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅${NC} npm: $NPM_VERSION"
else
    echo -e "${RED}❌${NC} npm not found"
fi
echo ""

echo "📦 NPM PACKAGES"
echo "────────────────────────────────────────────────────────────────"
if [ -d "$ROOT_DIR/kwd-dashboard/node_modules" ]; then
    echo -e "${GREEN}✅${NC} node_modules installed"
else
    echo -e "${YELLOW}⚠️${NC}  node_modules not found (run setup script to install)"
fi
echo ""

echo "✨ KEY FEATURES VERIFICATION"
echo "────────────────────────────────────────────────────────────────"

# Check for key features in server.py
if grep -q "def get_dashboard_data" "$ROOT_DIR/server.py"; then
    echo -e "${GREEN}✅${NC} API endpoint (/api/data) defined"
fi

if grep -q "def make_agg_month" "$ROOT_DIR/server.py"; then
    echo -e "${GREEN}✅${NC} Data aggregation functions"
fi

if grep -q "def compute_growth" "$ROOT_DIR/server.py"; then
    echo -e "${GREEN}✅${NC} Growth calculation functions"
fi

# Check for key features in keuangan.html
if grep -q "id=\"trendBarChart\"" "$ROOT_DIR/kwd-dashboard/src/html/keuangan.html"; then
    echo -e "${GREEN}✅${NC} Charts templates included"
fi

if grep -q "class=\"grid grid-cols-1\"" "$ROOT_DIR/kwd-dashboard/src/html/keuangan.html"; then
    echo -e "${GREEN}✅${NC} Responsive grid layout"
fi

if grep -q "UMKM" "$ROOT_DIR/kwd-dashboard/src/html/keuangan.html"; then
    echo -e "${GREEN}✅${NC} UMKM section included"
fi

if grep -q "loadDashboardData" "$ROOT_DIR/kwd-dashboard/src/html/keuangan.html"; then
    echo -e "${GREEN}✅${NC} API integration script"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ INTEGRATION VERIFICATION COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Run setup script: ./setup.sh (or setup.bat on Windows)"
echo "2. Read START_HERE.md for quick start guide"
echo "3. Follow development mode instructions"
echo "4. Access dashboard at: http://localhost:5000/keuangan"
echo ""
