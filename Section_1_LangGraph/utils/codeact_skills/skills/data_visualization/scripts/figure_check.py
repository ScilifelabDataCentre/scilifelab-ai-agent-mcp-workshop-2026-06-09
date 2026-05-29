"""Vision-LLM figure reviewer for the data_visualization skill.

Sends a saved figure to a vision-capable OpenAI model and returns five short
critiques covering Readability, Panel Arrangement, Axis Labels, Legend, and
Color. Designed to be called from `python_executor` inside the CodeAct agent.

Usage:
    from utils.codeact_skills.skills.data_visualization.scripts.figure_check import figure_check
    feedback = figure_check("my_plot.png")
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, model_validator

FIGURE_EVALUATION_SYSTEM_PROMPT = """You are a senior figure reviewer for a peer-reviewed life-sciences journal.
Evaluate the supplied figure against publication standards and return critical, actionable feedback on five dimensions:

  1. Readability       — font sizes, text overlap, contrast, ink economy.
  2. Panel Arrangement — panel ordering, spacing, sizing, panel labels (A/B/C).
  3. Axis Labels       — clarity, units in parentheses, tick legibility, presence of top/right spines.
  4. Legend            — placement, frame, font size, redundancy.
  5. Color             — colorblind safety (Wong 2011), colormap appropriateness, colorbar labels.

For each dimension write one or two concise sentences. If the figure is already correct on that dimension, say so briefly.

Respond with a SINGLE JSON object and nothing else, using exactly these keys:
{
  "Readability": "...",
  "Panel Arrangement": "...",
  "Axis Labels": "...",
  "Legend": "...",
  "Color": "..."
}
"""


class FigureFeedback(BaseModel):
    """Structured output from the figure-evaluation LLM."""

    Readability: str = Field(default="No feedback provided.")
    Panel_Arrangement: str = Field(default="No feedback provided.", alias="Panel Arrangement")
    Axis_Labels: str = Field(default="No feedback provided.", alias="Axis Labels")
    Legend: str = Field(default="No feedback provided.")
    Color: str = Field(default="No feedback provided.")

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _fill_blanks(cls, values: dict) -> dict:
        fallback = "No feedback provided."
        return {
            k: (v if isinstance(v, str) and v.strip() else fallback)
            for k, v in values.items()
        }

    def to_dict(self) -> dict[str, str]:
        return {
            "Readability": self.Readability,
            "Panel Arrangement": self.Panel_Arrangement,
            "Axis Labels": self.Axis_Labels,
            "Legend": self.Legend,
            "Color": self.Color,
        }


_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _encode_image(path: Path) -> tuple[str, str]:
    media_type = _MEDIA_TYPES.get(path.suffix.lower(), "image/png")
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return data, media_type


def _parse(raw: str) -> FigureFeedback:
    """Tolerant JSON parser — strips code fences, falls back to brace slice."""
    clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    data: dict = {}
    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        start, end = clean.find("{"), clean.rfind("}")
        if 0 <= start < end:
            try:
                data = json.loads(clean[start:end + 1])
            except json.JSONDecodeError:
                data = {}
    return FigureFeedback.model_validate(data)


def figure_check(figure_path: str, model: str = "gpt-5") -> dict[str, str]:
    """Evaluate a saved figure on five publication-quality dimensions.

    Args:
        figure_path: Path to a PNG/JPG/SVG/etc. figure file.
        model: Vision-capable OpenAI model name.

    Returns:
        A dict with keys: "Readability", "Panel Arrangement",
        "Axis Labels", "Legend", "Color". Each value is a short critique.
    """
    path = Path(figure_path)
    if not path.exists():
        raise FileNotFoundError(f"Figure not found: {figure_path}")

    image_data, media_type = _encode_image(path)

    llm = ChatOpenAI(model=model, temperature=0)
    messages = [
        SystemMessage(content=FIGURE_EVALUATION_SYSTEM_PROMPT),
        HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{image_data}",
                    "detail": "high",
                },
            },
            {
                "type": "text",
                "text": "Evaluate this figure against the publication standards in the system prompt. Return ONLY the JSON object.",
            },
        ]),
    ]
    raw = llm.invoke(messages).content
    return _parse(raw).to_dict()
