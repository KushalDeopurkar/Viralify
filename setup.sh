#!/bin/bash
set -e

echo "=== Viralify Setup ==="
echo ""

# Backend
echo "→ Setting up backend..."
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "  Backend deps installed."

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created backend/.env — fill in your API keys."
fi

cd ..

# Frontend
echo "→ Setting up frontend..."
cd frontend
npm install --silent 2>/dev/null || npm install
echo "  Frontend deps installed."

# Create .env.local from example if it doesn't exist
if [ ! -f .env.local ]; then
    cp .env.local.example .env.local
    echo "  Created frontend/.env.local"
fi

cd ..

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Get a free Gemini API key: https://ai.google.dev"
echo "  2. Get a free Groq API key:   https://console.groq.com"
echo "  3. Add them to backend/.env"
echo ""
echo "Then run:"
echo "  Terminal 1:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "  Terminal 2:  cd frontend && npm run dev"
echo "  Open:        http://localhost:3000"
