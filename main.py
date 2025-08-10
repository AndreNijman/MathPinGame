from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Callable, Iterable, List, Tuple

__all__ = [
    "generate_candidates",
    "compute_feedback",
    "filter_candidates",
    "initial_guess",
    "select_next_guess",
    "solve",
    "interactive_feedback_factory",
    "play",
]


def generate_candidates(length: int) -> List[str]:
    """Generate every possible pin of the given length."""
    digits = '0123456789'
    return [''.join(p) for p in product(digits, repeat=length)]


def compute_feedback(secret: str, guess: str) -> Tuple[int, int, int]:
    """Return feedback tuple for a guess against the secret.

    The tuple contains:
        * number of digits in the correct position
        * number of correct digits but in the wrong position
        * number of incorrect digits
    """
    correct_position = sum(s == g for s, g in zip(secret, guess))
    secret_counts = Counter(secret)
    guess_counts = Counter(guess)
    common = sum(min(secret_counts[d], guess_counts[d]) for d in secret_counts)
    correct_wrong_place = common - correct_position
    incorrect = len(secret) - common
    return correct_position, correct_wrong_place, incorrect


def filter_candidates(
    candidates: Iterable[str],
    guess: str,
    feedback: Tuple[int, int, int],
) -> List[str]:
    """Filter possible candidates using the feedback from a guess."""
    return [cand for cand in candidates if compute_feedback(cand, guess) == feedback]


def initial_guess(length: int) -> str:
    """Return the initial guess following a predictable pattern."""
    return ''.join(str(i % 10) for i in range(length))


def select_next_guess(candidates: List[str]) -> str:
    """Choose the next guess from remaining candidates.

    We prefer guesses with many unique digits to maximise the information we get
    from the next round of feedback.
    """
    return max(candidates, key=lambda c: (len(set(c)), c))


def solve(
    length: int,
    feedback_func: Callable[[str], Tuple[int, int, int]],
    return_guess: bool = False,
):
    """Solve the pin using the supplied feedback provider.

    Args:
        length: length of the pin being solved.
        feedback_func: callable receiving a guess string and returning a
            feedback tuple ``(correct_position, correct_wrong_place, incorrect)``.
        return_guess: if True, also return the final pin that was guessed.

    Returns:
        The number of attempts it took to deduce the pin.  If ``return_guess`` is
        True the guessed pin is returned as a second value.
    """
    candidates = generate_candidates(length)
    guess = initial_guess(length)
    attempts = 0

    while True:
        attempts += 1
        cp, cw, ci = feedback_func(guess)
        if cp == length:
            return (attempts, guess) if return_guess else attempts
        candidates = filter_candidates(candidates, guess, (cp, cw, ci))
        if not candidates:
            raise ValueError("No possible pins match the provided feedback.")
        guess = select_next_guess(candidates)


def interactive_feedback_factory(length: int) -> Callable[[str], Tuple[int, int, int]]:
    """Create a feedback provider that reads responses from the user.

    The provider prints the solver's guess and asks the user to supply
    feedback describing how many digits are correct and in the correct or
    incorrect positions.  Enter two numbers (``correct_pos`` and
    ``correct_wrong``) or three numbers if you also wish to specify the
    number of incorrect digits.  Type ``q`` to quit.
    """

    attempt = 0

    def provider(guess: str) -> Tuple[int, int, int]:
        nonlocal attempt
        attempt += 1
        print(f"\nAttempt {attempt}: my guess is {guess}")
        print(
            "Enter feedback as 'correct_pos correct_wrong [incorrect]'"
            " (e.g. '2 1' or '2 1 1'), or 'q' to quit:"
        )
        while True:
            raw = input(" > ").strip().lower()
            if raw in {"q", "quit", "exit"}:
                raise SystemExit("Game aborted by user.")
            parts = raw.split()
            try:
                if len(parts) == 2:
                    cp, cw = map(int, parts)
                    ci = length - cp - cw
                elif len(parts) == 3:
                    cp, cw, ci = map(int, parts)
                else:
                    raise ValueError
            except ValueError:
                print("Invalid feedback, try again.")
                continue
            if cp + cw + ci != length:
                print("Counts do not sum to the pin length, try again.")
                continue
            return cp, cw, ci

    return provider


def play() -> None:
    """Play an interactive game with the user."""
    print("PIN Cracker - think of a secret PIN and I'll try to guess it!")
    length = int(input("Enter pin length: ").strip())
    provider = interactive_feedback_factory(length)
    attempts, guess = solve(length, provider, return_guess=True)
    print(f"\nSecret pin {guess} cracked in {attempts} attempts!")

if __name__ == "__main__":
    play()