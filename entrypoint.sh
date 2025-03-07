#!/bin/bash
set -e

sleep 5

echo "🚀 Démarrage de FastAPI..."
exec python3 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
