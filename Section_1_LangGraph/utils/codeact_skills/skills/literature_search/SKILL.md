---
name: literature_search
description: Search PubMed for relevant passages on a biomedical topic using the NCBI LitSense2 semantic-search API. Returns ranked text snippets with their PMIDs.
---

# Literature search (LitSense)

`LitSense_API` is a thin wrapper around NCBI's LitSense2 endpoint. Give it a natural-language query (e.g. *"antiviral drugs that inhibit SARS-CoV-2 main protease"*) and it returns short passages from PubMed/PMC papers, each with a relevance score and PMID.

Use this skill when the user asks *what is known about*, *mechanism of action*, *clinical evidence*, *drug indication*, etc.

## Example implementation

```python
from utils.litsense.litsense import LitSense_API

def search_literature(query: str, limit: int = 5, rerank: bool = False) -> list[dict]:
    """Return up to `limit` PubMed passages relevant to the query."""
    engine = LitSense_API()
    results = engine.retrieve(query, limit=limit, rerank=rerank)
    if not results or isinstance(results, dict) and "error" in results:
        return []
    return [
        {"pmid": r.pmid, "score": r.score, "text": r.text}
        for r in results
    ]

# Quick usage
hits = search_literature("aspirin mechanism of action inflammation", limit=3)
for h in hits:
    print(f"PMID {h['pmid']} (score={h['score']:.2f}): {h['text'][:200]}...")
```

## Tips

- Keep queries focused — one biomedical concept per call works better than a long sentence.
- The `score` reflects semantic relevance after reranking; passages near the top are usually the most useful.
- Always cite results to the user as `PMID: <number>` so they can look up the source.
