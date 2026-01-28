#!/bin/bash

# Healthcare AI Service - Project Verification Script
# This script verifies the project structure and helps with initial setup

set -e

echo "=========================================="
echo "Healthcare AI Service - Project Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
    
    # Check if version is 3.9+
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        echo -e "${RED}✗${NC} Python 3.9+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi
echo ""

# Check project structure
echo "Checking project structure..."
REQUIRED_FILES=(
    "app/__init__.py"
    "app/main.py"
    "app/models.py"
    "app/logging.py"
    "app/config.py"
    "tests/__init__.py"
    "tests/test_api.py"
    "tests/test_logging.py"
    "requirements.txt"
    "README.md"
    "Dockerfile"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        ALL_PRESENT=false
    fi
done
echo ""

if [ "$ALL_PRESENT" = false ]; then
    echo -e "${RED}Some required files are missing!${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}!${NC} Virtual environment not found"
    echo "  Run: python3 -m venv venv"
fi
echo ""

# Check if dependencies are installed (if venv is active)
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Checking dependencies (virtual environment is active)..."
    
    if python3 -c "import fastapi" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} FastAPI installed"
    else
        echo -e "${RED}✗${NC} FastAPI not installed"
        echo "  Run: pip install -r requirements.txt"
    fi
    
    if python3 -c "import uvicorn" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Uvicorn installed"
    else
        echo -e "${RED}✗${NC} Uvicorn not installed"
        echo "  Run: pip install -r requirements.txt"
    fi
    
    if python3 -c "import pydantic" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Pydantic installed"
    else
        echo -e "${RED}✗${NC} Pydantic not installed"
        echo "  Run: pip install -r requirements.txt"
    fi
else
    echo -e "${YELLOW}!${NC} Virtual environment not activated"
    echo "  Activate with: source venv/bin/activate"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create and activate virtual environment (if not done):"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo ""
echo "2. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Run the service:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit the API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Run tests:"
echo "   pip install -r requirements-dev.txt"
echo "   pytest"
echo ""
echo "For more details, see:"
echo "- README.md - Project overview"
echo "- docs/QUICKSTART.md - Quick start guide"
echo "- docs/architecture.md - Architecture documentation"
echo ""
