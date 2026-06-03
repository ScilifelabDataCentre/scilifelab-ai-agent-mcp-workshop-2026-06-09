# ═══════════════════════════════════════════════════════════════════════════════
# sdk_advanced_client.py
# ═══════════════════════════════════════════════════════════════════════════════
# Run:  python sdk_advanced_client.py
# Requires mcp_advanced_server.py running on http://localhost:8501
# Set OPENAI_API_KEY in .env to enable the sampling demo.

# Save as a separate file, split at the line above when copying.

import asyncio, json, os
from typing import Any
from dotenv import load_dotenv
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

load_dotenv()
SERVER = "http://localhost:8501/mcp"

# ── LLM provider: self-hosted open-llm by default, OpenAI as fallback ──
from openai import (OpenAI, APIConnectionError, AuthenticationError,
                    PermissionDeniedError, InternalServerError)

FALLBACK_ERRORS = (APIConnectionError, AuthenticationError,
                   PermissionDeniedError, InternalServerError)
PROVIDERS = [
    {"name": "open-llm",
     "base_url": os.getenv("OPENLLM_BASE_URL", "https://open-llm.scilifelab.se/api"),
     "api_key":  os.getenv("OPENLLM_API_KEY"),
     "model":    os.getenv("OPENLLM_MODEL", "qwen3")},
    {"name": "openai", "base_url": None,
     "api_key": os.getenv("OPENAI_API_KEY"), "model": "gpt-4o"},
]
PROVIDERS = [p for p in PROVIDERS if p["api_key"]]


def chat_completion(messages, **kwargs):
    last = None
    for p in PROVIDERS:
        try:
            client = OpenAI(api_key=p["api_key"], base_url=p["base_url"])

            call_kwargs = dict(kwargs)
            if p["name"] == "open-llm":                       # qwen3 only
                call_kwargs["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}
                }
            # OpenAI fallback: extra_body is NOT added

            return client.chat.completions.create(
                model=p["model"], messages=messages, **call_kwargs
            )
        except FALLBACK_ERRORS as e:
            print(f"  [{p['name']}] {type(e).__name__} — falling back")
            last = e
    raise RuntimeError("No LLM provider reachable") from last

def _text(obj):
    for item in getattr(obj, "contents", None) or getattr(obj, "content", []):
        if hasattr(item, "text") and item.text: return item.text
        if hasattr(item, "blob"): return item.blob.decode()
    return str(obj)

async def main():
    async with streamablehttp_client(SERVER) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            print("Advanced session initialised.\n")

            # 1. resolve_smiles
            print("1. resolve_smiles(ERLOTINIB)")
            print(_text(await session.call_tool("resolve_smiles",
                        arguments={"drug_id": "ERLOTINIB"})), "\n")

            # 2. get_properties
            print("2. get_properties(erlotinib SMILES)")
            smiles = "C#Cc1cccc(Nc2ncnc3cc(OCCO)c(OCCO)cc23)c1"
            print(_text(await session.call_tool("get_properties",
                        arguments={"smiles": smiles})), "\n")

            # 3. Elicitation — find_drug
            print("3. find_drug(aspirin)  [elicitation]")
            raw = _text(await session.call_tool("find_drug",
                        arguments={"drug_name": "aspirin"}))
            data = json.loads(raw)
            if data.get("result_type") == "elicitation":
                print("  Server asks for clarification:", data["message"])
                for c in data["choices"]:
                    print("   -", c["label"], "->", c["value"])
                selected = data["choices"][0]["value"]
                print("  Auto-selecting:", selected)
                print(_text(await session.call_tool("get_drug_info",
                            arguments={"drug_id": selected})))
            print()

            # 4. Sampling: get_drug_hypothesis + optional LLM
            print("4. get_drug_hypothesis(IMATINIB)  [sampling]")
            raw = _text(await session.call_tool("get_drug_hypothesis",
                        arguments={"drug_id": "IMATINIB"}))
            payload = json.loads(raw)
            print("  Prompt (first 160 chars):", payload["prompt"][:160], "...\n")

            if PROVIDERS:
                completion = chat_completion(
                    [{"role": "user", "content": payload["prompt"]}],
                        max_tokens=2048,)
                
                msg = completion.choices[0].message
                hypothesis = (msg.content or "").strip()
                if not hypothesis:
                    fr = completion.choices[0].finish_reason
                    print(f"  LLM returned no content (finish_reason={fr}); skipping submit.\n")
                else:
                    print("  LLM hypothesis:", hypothesis, "\n")
                    submit = _text(await session.call_tool("submit_hypothesis_result",
                        arguments={"callback_token": payload["callback_token"],
                        "llm_result": hypothesis}))
                    print("  Callback:", json.loads(submit)["status"], "\n")
                
            else:
                print("  (Set OPENLLM_API_KEY or OPENAI_API_KEY to complete the hypothesis)\n")

            # 5. Streaming: stream_drug_analysis
            print("5. stream_drug_analysis(DASATINIB)  [streaming + progress]")
            result = _text(await session.call_tool("stream_drug_analysis",
                           arguments={"drug_id": "DASATINIB"}))
            print(result, "\n")

            # 6. Guardrail: blocked compound
            print("6. Guardrail — blocked compound (heroin)")
            try:
                await session.call_tool("get_drug_info", arguments={"drug_id": "heroin"})
            except Exception as e:
                print("  Correctly blocked:", e, "\n")

            # 7. Guardrail: invalid SMILES
            print("7. Guardrail — empty SMILES")
            try:
                await session.call_tool("get_properties", arguments={"smiles": ""})
            except Exception as e:
                print("  Correctly rejected:", e, "\n")
                
            # 8. lit_search
            print("8. lit_search — EGFR inhibitors")
            raw = _text(await session.call_tool("lit_search",
                        arguments={"query": "EGFR tyrosine kinase inhibitor",
                                   "max_results": 5}))
            hits = json.loads(raw)
            if 'error' in hits:
                print("  LitSense search failed:", hits['error'])
            else:
                print(f"  {hits['count']} result(s):")
                counter=0
                for h in hits.get("results", []):
                    counter+=1
                    print(counter)
                    print(' PMID:  ' + str(h['pmid']))
                    print(' Text:  ' + str(h['title']))
                    print(' Annotations:  ' + str(h['annotations']))
                    print()

if __name__ == "__main__":
    asyncio.run(main())
