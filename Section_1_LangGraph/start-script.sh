#!/bin/bash
set -e

ENV_FILE=/home/workshop/app/.env

# Build .env from environment variables provided at runtime.
# The SciLifeLab pilot LLM service is used by default; OpenAI is the fallback.
: > "$ENV_FILE"

# SciLifeLab pilot service key (default LLM). Falls back to the workshop
# shared key if no PILOT_API_KEY is provided at runtime.
PILOT_API_KEY="${PILOT_API_KEY:-sk-6967dda1dcf34427a00b352b31f1ca20}"
echo "PILOT_API_KEY=\"$PILOT_API_KEY\"" >> "$ENV_FILE"
echo "✓ PILOT_API_KEY written to .env"

# OpenAI key (fallback LLM). Only written if provided.
if [ -n "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> "$ENV_FILE"
    echo "✓ OPENAI_API_KEY written to .env"
else
    echo "⚠  No OPENAI_API_KEY set (OpenAI fallback will be unavailable)."
fi

echo ""
echo "============================================================"
echo "  Developing AI Agents in Life Sciences, Hands-on Session 1:"
echo "  Developing AI agents with LangGraph & ReAct"
echo "  2026-03-05"
echo "  Open: http://localhost:8888"
echo "  Then open: Section_1_LangGraph/langgraph_lab.ipynb"
echo "============================================================"
echo ""

python -m jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --notebook-dir=/home/workshop/app