#!/bin/bash

set -e

echo "🚀 Starting project setup..."

# 1. Python venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 2. Install requirements
if [ -f "requirements.txt" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, skipping..."
fi

# 3. Install Ollama if missing
if ! command -v ollama &> /dev/null
then
    echo "🤖 Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# 4. Pull model
MODEL="llama3.1:8b-instruct-q4_K_M"

echo "🧠 Checking model: $MODEL"

if ! ollama show "$MODEL" &> /dev/null; then
    echo "⬇️ Pulling model..."
    ollama pull "$MODEL"
else
    echo "✅ Model already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo "👉 Activate env: source venv/bin/activate"
echo "👉 Run your app as usual"