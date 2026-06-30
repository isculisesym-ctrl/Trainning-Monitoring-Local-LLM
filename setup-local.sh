#!/bin/bash
# Local Development Setup Script
# Run this once to set up your development environment

set -e

echo "=========================================="
echo "Training Dashboard - Local Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"

# Create required directories
mkdir -p data/logs
mkdir -p tests
echo "✓ Required directories created"

# Create local config if needed
if [ ! -f ".env.local" ]; then
    cat > .env.local << 'EOF'
# Local development configuration
DEBUG=true
LOG_LEVEL=INFO
DASHBOARD_PORT=3000
EOF
    echo "✓ Created .env.local (add your local secrets here)"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start dashboard (Terminal 1):"
echo "     python src/server/app.py"
echo ""
echo "  3. Run example (Terminal 2):"
echo "     python community/examples/training_simulator.py"
echo ""
echo "  4. Open dashboard:"
echo "     http://localhost:3000"
echo ""
echo "For Windows:"
echo "  - Use: venv\\Scripts\\activate"
echo "  - Or: .\\venv\\Scripts\\Activate.ps1 (PowerShell)"
echo ""
