#!/bin/bash
set -e

REPO_DIR=/home/workshop/app/repo

# Subdirectories that need .env access
SUBDIRS=(
    "$REPO_DIR/1-mcp-from-scratch"
    "$REPO_DIR/2-bonus-mcp-sdk-implementation"
    "$REPO_DIR/3-bonus-mcp-serve-app-integration"
)

# Write .env from environment variables (self-hosted open-llm by default, OpenAI optional)
ENV_LINES="OPENLLM_BASE_URL=\"${OPENLLM_BASE_URL:-https://open-llm.scilifelab.se/api}\"\n"
ENV_LINES+="OPENLLM_MODEL=\"${OPENLLM_MODEL:-qwen3}\"\n"
[ -n "$OPENLLM_API_KEY" ] && ENV_LINES+="OPENLLM_API_KEY=\"$OPENLLM_API_KEY\"\n"
[ -n "$OPENAI_API_KEY" ]  && ENV_LINES+="OPENAI_API_KEY=\"$OPENAI_API_KEY\"\n"
ENV_CONTENT=$(printf "%b" "$ENV_LINES")

if [ -n "$OPENLLM_API_KEY" ]; then
    echo "✓ OPENLLM_API_KEY provided (self-hosted open-llm)"
fi
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OPENAI_API_KEY provided (fallback)"
fi
if [ -z "$OPENLLM_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠  No OPENLLM_API_KEY or OPENAI_API_KEY set. Parts 5.3 and 6 require one."
    echo "   Edit the .env file in any subdirectory to add a key."
fi

# Write to repo root
echo "$ENV_CONTENT" > "$REPO_DIR/.env"
echo "  .env written to $REPO_DIR/"

# Write to each subdirectory so scripts run from there can find it
for dir in "${SUBDIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "$ENV_CONTENT" > "$dir/.env"
        echo "  .env written to $dir/"
    else
        echo "⚠  Directory not found, skipping: $dir"
    fi
done

echo ""
echo "============================================================"
echo "  Workshop: Developing AI Agents in Life Sciences (Gothenburg), SciLifeLab Data Centre"
echo "  Korallrevet, Natrium, Medicinaregatan 7B, Gothenburg"
echo "  Hands-on Session 2:"
echo "  AI agent collaboration with the Model Context Protocol (MCP)"
echo "  2026-06-09"
echo "  Open: http://localhost:7860"
echo "  Then open: 1-mcp-from-scratch/mcp_workshop.ipynb"
echo "============================================================"
echo ""

python3 -m jupyter lab \
    --ip=0.0.0.0 \
    --port=7860 \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --notebook-dir="$REPO_DIR"