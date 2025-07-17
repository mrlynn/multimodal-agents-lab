#!/bin/bash

echo "🚀 Multimodal Agents Lab - Codespace Setup"
echo "=========================================="

# Check if running in Codespaces
if [ -z "$CODESPACES" ]; then
    echo "⚠️  This script is designed for GitHub Codespaces"
    echo "   But can also work in local environments"
fi

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file template..."
    cat > .env << 'EOF'
# Multimodal Agents Lab Environment Variables

# MongoDB Connection (provided by Codespaces)
MONGODB_URI="mongodb://admin:mongodb@mongodb:27017/"

# Serverless URL (provided)
SERVERLESS_URL="https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/"

# Google Gemini API Key (required)
# Get yours at: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY="your-google-api-key-here"

# Voyage AI API Key (optional - will use free tier if not provided)
# Get yours at: https://www.voyageai.com/
VOYAGE_API_KEY=""
EOF
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your Google API key!"
    echo "   1. Get an API key from: https://makersuite.google.com/app/apikey"
    echo "   2. Edit the .env file and replace 'your-google-api-key-here'"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check Google API key
if [ "$GOOGLE_API_KEY" = "your-google-api-key-here" ] || [ -z "$GOOGLE_API_KEY" ]; then
    echo ""
    echo "❌ Google API key not configured!"
    echo "   Please edit .env and add your API key"
    echo ""
    echo "To get started:"
    echo "1. Open .env file"
    echo "2. Replace 'your-google-api-key-here' with your actual API key"
    echo "3. Run this script again: ./setup_codespace.sh"
else
    echo "✅ Google API key is configured"
fi

# Install Python requirements
echo ""
echo "📦 Installing Python requirements..."
pip install --user -r requirements.txt

# Test Python environment
echo ""
echo "🐍 Testing Python environment..."
python -c "import google.generativeai; print('✅ Google AI SDK installed')"
python -c "import pymongo; print('✅ PyMongo installed')"
python -c "import voyageai; print('✅ Voyage AI SDK installed')"

# Run debug script
echo ""
echo "🔍 Running system diagnostics..."
python debug_notebook.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure all checks above passed"
echo "2. Open Jupyter Lab: jupyter lab"
echo "3. Open the lab.ipynb notebook"
echo "4. Run the cells in order"
echo ""
echo "For debugging, use:"
echo "- debug_helpers.ipynb - Interactive debugging notebook"
echo "- python debug_notebook.py - Command line diagnostics"