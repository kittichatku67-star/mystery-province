"""Basic regression tests for Mystery Province game logic."""

from questions import QUESTIONS, get_question
from scoring import GameState, calculate_score


def run_tests():
    assert len(QUESTIONS) >= 5
    assert get_question(1)["answer"] == "เชียงใหม่"
    assert get_question(999) is None

    game = GameState(QUESTIONS[0])
    assert game.score == 100
    assert game.attempts == 0
    assert game.submit_guess("กรุงเทพมหานคร") is False
    assert game.attempts == 1
    assert game.wrong_guesses == 1
    assert game.is_finished is False
    assert game.score == 100

    assert game.use_hint() == QUESTIONS[0]["hint"]
    assert game.score == 80
    assert game.use_hint() is None

    assert game.submit_guess("เชียงใหม่") is True
    assert game.is_finished is True
    assert game.is_correct is True
    assert game.attempts == 2

    assert game.submit_guess("ภูเก็ต") is True
    assert game.attempts == 2

    assert calculate_score(0) == 100
    assert calculate_score(1) == 80
    assert calculate_score(5) == 0

    print("STEP 5 Game Logic: PASS")
    print(f"Questions: {len(QUESTIONS)}")
    print("Wrong guess -> retry: PASS")
    print("Hint penalty: PASS")
    print("Correct guess -> finish: PASS")
    print("Duplicate submission after finish: PASS")


if __name__ == "__main__":
    run_tests()
