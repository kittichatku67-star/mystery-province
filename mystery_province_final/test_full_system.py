"""End-to-end regression checks for Mystery Province."""

import ast
import csv
from pathlib import Path

from gensim.models import Word2Vec

from game.scoring import GameState
from ir.search_engine import ProvinceSearchEngine

BASE_DIR = Path(__file__).resolve().parent


def main():
    # 1) Dataset integrity
    with open(BASE_DIR / "data" / "provinces.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 77
    assert len({row["province"] for row in rows}) == 77
    assert all(all(value.strip() for value in row.values()) for row in rows)

    # 2) Word2Vec model integrity
    model = Word2Vec.load(str(BASE_DIR / "models" / "word2vec.model"))
    assert len(model.wv) == 967
    assert model.vector_size == 100

    # 3) IR search regression
    engine = ProvinceSearchEngine()
    queries = [
        "ภูเขา ดอย หนาว กาแฟ",
        "ทะเล ชายหาด เกาะ อาหารทะเล",
        "อีสาน ข้าวเหนียว หมอลำ ผ้าไหม",
        "วัด ทะเล แม่น้ำ อาหาร",
        "ประเพณี ล้านนา ดอย วัฒนธรรม",
    ]
    for query in queries:
        result = engine.search(query, top_k=10)
        assert len(result["results"]) == 10
        scores = [item["score"] for item in result["results"]]
        assert scores == sorted(scores, reverse=True)
        assert len({item["province"] for item in result["results"]}) == 10

    # 4) Edge cases
    assert engine.search("")["results"] == []
    assert engine.search("xyzabc123")["results"] == []

    # 5) Game flow
    game = GameState(question={"answer": "เชียงใหม่", "hint": "อยู่ภาคเหนือ"})
    assert game.submit_guess("เชียงราย") is False
    assert game.attempts == 1
    assert game.use_hint() == "อยู่ภาคเหนือ"
    assert game.score == 80
    assert game.submit_guess("เชียงใหม่") is True
    assert game.is_finished is True
    assert game.submit_guess("เชียงใหม่") is True

    # 6) app.py syntax / parse check
    ast.parse((BASE_DIR / "app.py").read_text(encoding="utf-8"))

    print("STEP 9 FULL SYSTEM TEST: PASS")
    print("Dataset: 77 provinces")
    print("Word2Vec: 967 words / 100 dimensions")
    print("Search: 5 queries + edge cases PASS")
    print("Game: wrong -> hint -> correct flow PASS")
    print("Streamlit app syntax: PASS")
    print("Note: browser smoke test requires Streamlit installed")


if __name__ == "__main__":
    main()
