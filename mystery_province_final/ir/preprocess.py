"""Text preprocessing for the Mystery Province IR project."""

import re
from typing import Iterable

import pandas as pd

TEXT_COLUMNS = [
    "province",
    "region",
    "description",
    "landmark",
    "food",
    "culture",
    "geography",
    "keywords",
]


def normalize_text(text: str) -> str:
    """Normalize text while keeping Thai characters and useful separators."""
    text = str(text).strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[\[\]{}()\"'`!?.,:;/\\]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_text(text: str) -> list[str]:
    """Tokenize project text without adding an external Thai NLP dependency.

    The dataset uses | to separate individual concepts. Spaces are also treated
    as token boundaries, making the vocabulary easy to inspect in class.
    """
    text = normalize_text(text)
    text = text.replace("|", " ")
    return [token for token in text.split() if token]


def row_to_tokens(row: pd.Series) -> list[str]:
    """Convert one province row into a Word2Vec training sentence."""
    tokens: list[str] = []
    for column in TEXT_COLUMNS:
        tokens.extend(tokenize_text(row[column]))
    return tokens


def build_corpus(csv_path: str) -> list[list[str]]:
    """Load provinces.csv and return one tokenized sentence per province."""
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing = [column for column in TEXT_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    corpus = [row_to_tokens(row) for _, row in df.iterrows()]
    if not corpus:
        raise ValueError("Dataset is empty")
    return corpus


def tokenize_query(query: str) -> list[str]:
    """Tokenize a player's search query."""
    return tokenize_text(query)
