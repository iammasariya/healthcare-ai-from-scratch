#!/bin/bash
# Healthcare AI Service - Automated Setup Script
# This script sets up the project for development or testing

set -e  # Exit on error

echo "=========================================="
echo "Healthcare AI Service - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ] || [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_error "Could not find virtual environment activation script"
    exit 1
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded"

# Install dependencies
echo ""
echo "Installing production dependencies..."
pip install -r requirements.txt
print_success "Production dependencies installed"

echo ""
read -p "Install development dependencies? (pytest, black, etc.) [y/N]: " install_dev
if [[ $install_dev =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
    print_success "Development dependencies installed"
fi

# Set up .env file
echo ""
if [ -f ".env" ]; then
    print_warning ".env file already exists. Skipping creation."
else
    echo "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "Remember to update .env with your actual configuration!"
fi

# Create prompts directory if it doesn't exist
echo ""
if [ -d "prompts" ]; then
    print_success "prompts/ directory exists"
else
    echo "Creating prompts directory..."
    mkdir -p prompts
    print_success "prompts/ directory created"
fi

# Verify prompts exist
if [ -f "prompts/clinical_summarization_v1.0.0.yaml" ]; then
    print_success "Clinical summarization prompt found"
else
    print_warning "No prompts found in prompts/ directory"
    echo "    You may need to create prompt YAML files"
fi

# Run tests
echo ""
read -p "Run test suite to verify installation? [Y/n]: " run_tests
if [[ ! $run_tests =~ ^[Nn]$ ]]; then
    echo ""
    echo "Running test suite..."
    python -m pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed. Please check the output above."
    fi
fi

# Run prompt verification
echo ""
read -p "Run prompt verification? [Y/n]: " verify_prompts
if [[ ! $verify_prompts =~ ^[Nn]$ ]]; then
    echo ""
    echo "Verifying prompt system..."
    python verify_prompts.py
fi

# Print next steps
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Update .env with your configuration:"
echo "   - Set ANTHROPIC_API_KEY if using LLM features"
echo "   - Adjust other settings as needed"
echo ""
echo "3. Start the development server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Try the example scripts:"
echo "   python examples/test_client.py"
echo "   python examples/test_summarize.py  # Requires API key"
echo ""
echo "For more information, see README.md"
echo ""