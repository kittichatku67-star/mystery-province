"""Scoring and game-state logic for Mystery Province."""

BASE_SCORE = 100
HINT_PENALTY = 20
WRONG_GUESS_PENALTY = 0


def normalize_answer(answer: str) -> str:
    """Normalize an answer for fair comparison."""
    return " ".join(answer.strip().lower().split())


def calculate_score(hints_used: int, wrong_guesses: int = 0) -> int:
    """Calculate score. Wrong guesses allow retry and do not reduce score."""
    score = BASE_SCORE - (hints_used * HINT_PENALTY)
    return max(score, 0)


class GameState:
    """Track attempts, hints, score, and answer state for one question."""

    def __init__(self, question: dict):
        self.question = question
        self.attempts = 0
        self.wrong_guesses = 0
        self.hints_used = 0
        self.is_correct = False
        self.is_finished = False

    @property
    def score(self) -> int:
        return calculate_score(self.hints_used, self.wrong_guesses)

    def use_hint(self) -> str | None:
        """Use the available hint once and return its text."""
        if self.hints_used >= 1 or self.is_finished:
            return None
        self.hints_used += 1
        return self.question["hint"]

    def submit_guess(self, guess: str) -> bool:
        """Submit a province guess and return whether it is correct."""
        if self.is_finished:
            return self.is_correct

        self.attempts += 1
        correct = normalize_answer(guess) == normalize_answer(self.question["answer"])

        if correct:
            self.is_correct = True
            self.is_finished = True
        else:
            self.wrong_guesses += 1

        return correct
