"""Utilities for demonstrating the Mystery Province IR pipeline."""

from __future__ import annotations

import numpy as np


def analyze_query(engine, query: str, top_k: int = 5) -> dict:
    """Return real intermediate IR data for an educational Streamlit demo."""
    result = engine.search(query, top_k=top_k)
    known_tokens = result["known_tokens"]
    query_vector = engine._average_vectors(known_tokens)

    token_vectors = []
    for token in known_tokens:
        vector = engine.model.wv[token]
        token_vectors.append(
            {
                "token": token,
                "vector": vector,
                "first_values": [float(value) for value in vector[:8]],
            }
        )

    top_province = result["results"][0]["province"] if result["results"] else None
    province_vector = (
        engine._province_vectors.get(top_province) if top_province else None
    )

    cosine_value = result["results"][0]["score"] if result["results"] else None

    return {
        "result": result,
        "query_vector": query_vector,
        "query_vector_first_values": (
            [float(value) for value in query_vector[:8]]
            if query_vector is not None
            else []
        ),
        "vector_size": engine.model.vector_size,
        "token_vectors": token_vectors,
        "top_province": top_province,
        "province_vector_first_values": (
            [float(value) for value in province_vector[:8]]
            if province_vector is not None
            else []
        ),
        "cosine_value": cosine_value,
        "province_count": len(engine._province_vectors),
        "vocabulary_size": len(engine.model.wv),
    }
