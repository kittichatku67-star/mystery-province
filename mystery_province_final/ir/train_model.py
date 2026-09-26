"""Train the project's Word2Vec model from the local province dataset."""

from pathlib import Path

from gensim.models import Word2Vec

try:
    from .preprocess import build_corpus
except ImportError:
    from preprocess import build_corpus

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "provinces.csv"
MODEL_PATH = BASE_DIR / "models" / "word2vec.model"


def train_word2vec(
    data_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
    vector_size: int = 100,
    window: int = 5,
    min_count: int = 1,
    workers: int = 4,
    epochs: int = 100,
) -> Word2Vec:
    """Train and save Word2Vec using only the project's own dataset."""
    corpus = build_corpus(str(data_path))

    model = Word2Vec(
        sentences=corpus,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=workers,
        epochs=epochs,
        sg=1,
        seed=42,
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    return model


if __name__ == "__main__":
    model = train_word2vec()
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Vocabulary size: {len(model.wv)}")
    for word in ["ภูเขา", "ดอย", "หนาว", "กาแฟ"]:
        if word in model.wv:
            print(f"{word}: found")
        else:
            print(f"{word}: NOT FOUND")
