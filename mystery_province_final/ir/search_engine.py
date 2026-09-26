"""Word2Vec-based province search engine for Mystery Province."""

from pathlib import Path

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .preprocess import tokenize_query, row_to_tokens
except ImportError:
    from preprocess import tokenize_query, row_to_tokens

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "provinces.csv"
MODEL_PATH = BASE_DIR / "models" / "word2vec.model"


class ProvinceSearchEngine:
    """Search Thai province data with Word2Vec and cosine similarity."""

    def __init__(self, model_path: Path = MODEL_PATH, data_path: Path = DATA_PATH):
        self.model = Word2Vec.load(str(model_path))
        self.data = pd.read_csv(data_path, encoding="utf-8-sig")
        self._province_vectors = self._build_province_vectors()

    def _average_vectors(self, tokens: list[str]) -> np.ndarray | None:
        """Return the mean Word2Vec vector for tokens in the vocabulary."""
        vectors = [self.model.wv[token] for token in tokens if token in self.model.wv]
        if not vectors:
            return None
        return np.mean(vectors, axis=0)

    def _build_province_vectors(self) -> dict[str, np.ndarray]:
        """Create one vector for each province by averaging its dataset words."""
        vectors = {}
        for _, row in self.data.iterrows():
            tokens = row_to_tokens(row)
            vector = self._average_vectors(tokens)
            if vector is not None:
                vectors[row["province"]] = vector
        return vectors

    def search(self, query: str, top_k: int = 10) -> dict:
        """Rank provinces for a natural-language Thai query."""
        tokens = tokenize_query(query)
        known_tokens = [token for token in tokens if token in self.model.wv]
        unknown_tokens = [token for token in tokens if token not in self.model.wv]

        query_vector = self._average_vectors(known_tokens)
        if query_vector is None:
            return {
                "query": query,
                "tokens": tokens,
                "known_tokens": [],
                "unknown_tokens": unknown_tokens,
                "results": [],
            }

        province_names = list(self._province_vectors.keys())
        province_matrix = np.vstack([self._province_vectors[name] for name in province_names])
        scores = cosine_similarity(query_vector.reshape(1, -1), province_matrix)[0]

        ranking = sorted(
            zip(province_names, scores), key=lambda item: item[1], reverse=True
        )[:top_k]

        results = [
            {"rank": rank, "province": province, "score": float(score)}
            for rank, (province, score) in enumerate(ranking, start=1)
        ]

        return {
            "query": query,
            "tokens": tokens,
            "known_tokens": known_tokens,
            "unknown_tokens": unknown_tokens,
            "results": results,
        }

    def rank_against_province(self, target_province: str) -> list[dict]:
        """Rank all provinces by similarity to a target province vector.

        Used by the game to give Contexto-style feedback without revealing
        the target province. Lower rank means the guessed province is more
        semantically similar to the hidden answer.
        """
        if target_province not in self._province_vectors:
            return []

        target_vector = self._province_vectors[target_province]
        province_names = list(self._province_vectors.keys())
        province_matrix = np.vstack([self._province_vectors[name] for name in province_names])
        scores = cosine_similarity(target_vector.reshape(1, -1), province_matrix)[0]

        ranking = sorted(
            zip(province_names, scores), key=lambda item: item[1], reverse=True
        )
        return [
            {"rank": rank, "province": province, "score": float(score)}
            for rank, (province, score) in enumerate(ranking, start=1)
        ]

    def get_contexto_feedback(self, target_province: str, guessed_province: str) -> dict | None:
        """Return rank/similarity/color for one guessed province."""
        ranking = self.rank_against_province(target_province)
        for item in ranking:
            if item["province"] == guessed_province:
                rank = item["rank"]
                if rank <= 10:
                    color, label = "green", "ใกล้มาก"
                elif rank <= 30:
                    color, label = "yellow", "ใกล้ปานกลาง"
                else:
                    color, label = "red", "ค่อนข้างไกล"
                return {**item, "color": color, "label": label}
        return None


def search_provinces(query: str, top_k: int = 10) -> dict:
    """Convenience function for Streamlit and simple testing."""
    engine = ProvinceSearchEngine()
    return engine.search(query, top_k=top_k)


if __name__ == "__main__":
    engine = ProvinceSearchEngine()
    test_queries = [
        "ภูเขา ดอย หนาว กาแฟ",
        "ทะเล ชายหาด เกาะ อาหารทะเล",
        "อีสาน ข้าวเหนียว หมอลำ ผ้าไหม",
        "วัด ทะเล แม่น้ำ อาหาร",
        "ประเพณี ล้านนา ดอย วัฒนธรรม",
    ]

    for query in test_queries:
        result = engine.search(query, top_k=5)
        print(f"\nQuery: {query}")
        print(f"Known: {result['known_tokens']}")
        print(f"Unknown: {result['unknown_tokens']}")
        for item in result["results"]:
            print(f"{item['rank']}. {item['province']} {item['score']:.4f}")
