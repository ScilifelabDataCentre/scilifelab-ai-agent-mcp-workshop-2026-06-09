# =============================================================================
# Dockerfile — Workshop: Developing AI Agents in Life Sciences (Gothenburg), SciLifeLab Data Centre · Korallrevet, Natrium, Medicinaregatan 7B, Gothenburg · 2026-06-09
# Compatible with both local Docker and SciLifeLab Serve
#
# Build context: session-2-mcp/
#
# Pull from dockerhub:
#   docker run -p 7860:7860 -e OPENLLM_API_KEY="sk-..." mahbub1969/scilifelab-mcp-workshop:v2
#
# Local:
#   docker build -t <your-dockerhub-account-name>/scilifelab-mcp-workshop:v2 .
#   docker run -p 7860:7860 -e OPENLLM_API_KEY="sk-..." <your-dockerhub-account-name>/scilifelab-mcp-workshop:v2
# Multi-arch: to ensure it runs on both Linux and Mac
#   docker buildx build --platform linux/amd64,linux/arm64 \
#       -t <your-dockerhub-account-name>/scilifelab-mcp-workshop:v1 --push .
#
# SciLifeLab Serve deployment (https://serve.scilifelab.se/):
#   Create a Custom app
#   Use Image: mahbub1969/scilifelab-mcp-workshop:v2
#   Set port to 7860
#   Make sure to provide API key
# =============================================================================

FROM python:3.14-slim

LABEL maintainer="SciLifeLab Data Centre <serve@scilifelab.se>"
LABEL description="Workshop: Developing AI Agents in Life Sciences (Gothenburg), SciLifeLab Data Centre · Korallrevet, Natrium, Medicinaregatan 7B, Gothenburg · 2026-06-09, Hands-on Session 2: AI agent collaboration with the Model Context Protocol (MCP)"

ENV DEBIAN_FRONTEND=noninteractive
ENV USER=workshop
ENV HOME=/home/$USER

# Create non-root user with uid 1000 (required by SciLifeLab Serve)
RUN useradd -m -u 1000 $USER

# System dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
        build-essential \
        libxrender1 \
        libxext6 \
        procps \
        lsof \
    && rm -rf /var/lib/apt/lists/*

# Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir jupyterlab ipywidgets \
    && rm /tmp/requirements.txt

# Set working directory
WORKDIR $HOME/app

# Workshop content — top-level files + subdirectories
COPY README.md                        $HOME/app/repo/README.md
COPY requirements.txt                 $HOME/app/repo/requirements.txt
COPY Dockerfile                       $HOME/app/repo/Dockerfile
COPY start-script.sh                  $HOME/app/repo/start-script.sh
COPY jupyter_lab_config.py            $HOME/app/repo/jupyter_lab_config.py
COPY 1-mcp-from-scratch/              $HOME/app/repo/1-mcp-from-scratch/
COPY 2-bonus-mcp-sdk-implementation/  $HOME/app/repo/2-bonus-mcp-sdk-implementation/
COPY 3-bonus-mcp-serve-app-integration/ $HOME/app/repo/3-bonus-mcp-serve-app-integration/

# Jupyter config (also at app level for JupyterLab to find it)
COPY jupyter_lab_config.py $HOME/app/jupyter_lab_config.py

# .env placeholder (start-script.sh writes real ones at runtime)
RUN echo '# Set OPENLLM_API_KEY (and optionally OPENAI_API_KEY) via docker run -e OPENLLM_API_KEY="sk-..."' > $HOME/app/repo/.env

# Start script (required by SciLifeLab Serve)
COPY start-script.sh $HOME/app/start-script.sh
RUN chmod +x $HOME/app/start-script.sh

# Fix ownership for non-root user
RUN chown -R $USER:$USER $HOME

USER $USER
EXPOSE 7860

ENTRYPOINT ["./start-script.sh"]