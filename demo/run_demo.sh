#!/bin/bash

# RMN LoRA Demo - Quick Start Script

set -e

echo "🚀 RMN LoRA System Demo Setup"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"

# Generate synthetic data
echo ""
echo "🎲 Generating synthetic data..."
python3 generate_synthetic_data.py
echo "   ✅ Data generated"

# Check if data was created
if [ -d "data" ]; then
    echo ""
    echo "📁 Data files created:"
    echo "   - $(ls -1 data/retailer_alpha/*.csv 2>/dev/null | wc -l) Alpha files"
    echo "   - $(ls -1 data/retailer_beta/*.jsonl 2>/dev/null | wc -l) Beta files"
    echo "   - $(ls -1 data/*.csv 2>/dev/null | wc -l) catalog files"
else
    echo "   ⚠️  Warning: Data directory not found"
fi

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "🎯 To start the demo:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "📖 Demo script:"
echo "   See DEMO_SCRIPT.md for 15-minute presenter guide"
echo ""
echo "🌐 Demo will open at:"
echo "   http://localhost:8501"
echo ""
