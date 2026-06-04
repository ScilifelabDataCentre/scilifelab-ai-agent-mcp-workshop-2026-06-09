# [Developing AI Agents in Life Sciences (Gothenburg)](https://www.scilifelab.se/event/ai-agents-in-life-science-gothenburg/)

## Hands-on Session 2: AI Agent Collaboration with the Model Context Protocol (MCP)

> **SciLifeLab Data Centre** · Korallrevet, Natrium, Medicinaregatan 7B, Gothenburg · 2026-06-09

---

## What you will build

In this session you expose the drug discovery tools from Session 1 over the **Model Context Protocol (MCP)**, a standardised layer that lets any AI application discover and call your tools dynamically. You will build an MCP server from scratch, add guardrails and security, and connect your LangGraph agent to it.

The workshop has three parts:

| Directory | What's inside | Type |
|---|---|---|
| `1-mcp-from-scratch/` | Main workshop notebook with 11 fill-in-the-blank gaps | **Core session** |
| `2-bonus-mcp-sdk-implementation/` | Same server re-implemented with the official MCP Python SDK | Optional bonus |
| `3-bonus-mcp-serve-app-integration/` | Wrapping a deployed SciLifeLab Serve ML model as an MCP server | Optional bonus |

Each directory has its own README with detailed instructions.

---

## Getting started

You need an **open-llm API key** (self-hosted — the default). An OpenAI key also works as an optional fallback. Have one ready before you start.

### Option 1: Pull from Docker Hub (recommended)

Everything is pre-installed. One command to start:

```bash
docker run -p 7860:7860 -e OPENLLM_API_KEY="sk-..." mahbub1969/scilifelab-gothenburg-workshop-mcp:v1
```

Then open **http://localhost:7860** in your browser and navigate to `1-mcp-from-scratch/mcp_workshop.ipynb`.

### Option 2: Build the image locally

```bash
# From the session-2-mcp/ directory
docker build -t scilifelab-gothenburg-workshop-mcp:v1 .
docker run -p 7860:7860 -e OPENLLM_API_KEY="sk-..." scilifelab-gothenburg-workshop-mcp:v1
```

Then open **http://localhost:7860** as above.

### Option 3: Deploy on SciLifeLab Serve (after the workshop)

> This option is for **after the workshop**, if you want to revisit the material or share it with colleagues without installing Docker locally. During the session, use Option 1 or 2.

If you are affiliated with a Swedish research institution, you can deploy this as a persistent app on [SciLifeLab Serve](https://serve.scilifelab.se/). Create a **Custom app**, set the image to `mahbub1969/scilifelab-gothenburg-workshop-mcp:v1`, port `7860`, and provide your API key in the `.env` file after.

For questions about Serve deployment, contact the SciLifeLab Serve team at **serve@scilifelab.se**.

---

## Running locally without Docker (not supported during the workshop)

> ⚠️ **Pulling pre-built images from Docker Hub is the only setup we will support during the workshop due to time constraints**. The local option is provided for your own reference after the session. We will not troubleshoot local environment issues during workshop.

If you prefer to run without Docker later:

```bash
# From the session-2-mcp/ directory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add your open-llm key (base URL and model are shown explicitly; both have defaults in the code)
for d in 1-mcp-from-scratch 2-bonus-mcp-sdk-implementation 3-bonus-mcp-serve-app-integration; do
  cat > "$d/.env" <<EOF
OPENLLM_API_KEY="sk-..."
OPENLLM_BASE_URL="https://open-llm.scilifelab.se/api"
OPENLLM_MODEL="qwen3"
EOF
done

# Open the notebook
cd 1-mcp-from-scratch/
jupyter lab
```

You will need Python 3.10+ and all packages listed in `requirements.txt`. RDKit is optional — the workshop falls back to pre-computed properties if it is not available.

---

## Directory structure

```
session-2-mcp/
├── README.md                              ← This file
├── Dockerfile
├── requirements.txt
├── start-script.sh
├── jupyter_lab_config.py
│
├── 1-mcp-from-scratch/                    ← Main workshop (start here)
│   ├── README.md
│   ├── mcp_workshop.ipynb                 ← Your main notebook
│   ├── mcp_workshop_answers.ipynb         ← Reference answers
│   ├── drug_db.json
│   ├── images/
│   └── ...
│
├── 2-bonus-mcp-sdk-implementation/        ← SDK bonus (optional)
│   ├── README.md
│   ├── sdk_basic_server.py
│   ├── sdk_advanced_server.py
│   └── ...
│
└── 3-bonus-mcp-serve-app-integration/     ← Serve app bonus (optional)
    ├── README.md
    ├── shamsul-mcp-server.py
    ├── agent-mediator.py
    └── ...
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Docker: `port is already allocated` | Stop any process using port 7860, or use `-p 8888:7860` and open port 8888 instead |
| Jupyter shows but no notebooks appear | Navigate into `1-mcp-from-scratch/` in the Jupyter file browser |
| LLM 401 / authentication error | Check that you passed `-e OPENLLM_API_KEY="sk-..."` (or `OPENAI_API_KEY` for the fallback) when starting the container |
| `Address already in use` on 8501/8502 | Another server is running on that port — stop it first (see the notebook README) |

For other issues, see the README inside each subdirectory.
