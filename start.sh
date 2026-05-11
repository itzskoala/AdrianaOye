#!/bin/bash
set -e

# Start FastAPI backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Gradio UI — keeps the container alive
python3 -m source.agent.app
