#!/bin/bash
# Quick setup script for development

echo "🚀 Setting up Horizon Blog..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ Please edit .env and add your Entra ID credentials"
else
    echo "✓ .env file exists"
fi

# Initialize database
if [ ! -f "blogsite.db" ]; then
    echo "Initializing database..."
    python init_db.py
    echo "✓ Database initialized"
    
    echo "Migrating existing posts..."
    python migrate_posts.py
    echo "✓ Posts migrated"
else
    echo "✓ Database exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then visit: http://localhost:5000"


