#!/bin/bash
# Novel Generation System - Interactive Runner

# Activate virtual environment
source /project/novel/venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=/project/novel:$PYTHONPATH

# Check if .env file exists
if [ ! -f /project/novel/.env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your ANTHROPIC_API_KEY"
    echo "Example:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your API key"
    exit 1
fi

# Load environment variables
set -a
source /project/novel/.env
set +a

# Display configuration (for debugging)
echo "📡 API Configuration:"
echo "   Base URL: ${ANTHROPIC_BASE_URL:-default}"
echo "   Auth Token: ${ANTHROPIC_AUTH_TOKEN:0:20}..."
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env file!"
    exit 1
fi

echo "🚀 Starting Novel Generation System..."
echo ""

# Run the main script with actual execution
python3 /project/novel/src/main.py "$@"
