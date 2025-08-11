"""Test helper and basic smoke tests for the PIN solver.

Running this module directly will execute a short demo so you can see the
solver in action and inspect the number of attempts it needs for a given
secret.
"""

from __future__ import annotations

import random
import sys

from main import compute_feedback, solve


def crack(secret: str):
    """Helper that runs ``solve`` against a known secret pin."""
    length = len(secret)
    provider = lambda guess: compute_feedback(secret, guess)
    return solve(length, provider, return_guess=True)


def test_four_digit_pin():
    attempts, guess = crack("0194")
    assert guess == "0194"from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Callable, Iterable, List, Sequence, Tuple

# Explicit re-export of the public API so ``from main import X`` works as
# expected.  This also guards against stale imports if the module is partially
# executed elsewhere.
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

    This implementation mirrors Mastermind's scoring: ``correct_position`` is
    the number of exact matches, ``correct_wrong_place`` counts the remaining
    digits that are present but misplaced and ``incorrect`` is the rest.  The
    version below uses fixed-size integer arrays instead of ``Counter`` for a
    noticeable speed-up when evaluating large candidate sets.
    """

    correct_position = sum(s == g for s, g in zip(secret, guess))
    secret_counts = [0] * 10
    guess_counts = [0] * 10
    for s in secret:
        secret_counts[ord(s) - 48] += 1
    for g in guess:
        guess_counts[ord(g) - 48] += 1
    common = sum(min(sc, gc) for sc, gc in zip(secret_counts, guess_counts))
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


def select_next_guess(
    candidates: Sequence[str],
    universe: Sequence[str],
    *,
    optimal: bool = False,
) -> str:
    """Return the next guess using a minimax Mastermind strategy.

    Parameters
    ----------
    candidates, universe:
        Current candidate codes and the full universe of possible codes.
    optimal:
        When ``True`` the entire search space is evaluated to choose the guess
        that minimises the worst-case number of remaining candidates.  This is
        effectively Knuth's original algorithm and can guarantee solutions in a
        fixed number of guesses (four for a four digit PIN) but is extremely
        slow as it requires scoring every possible guess against every
        candidate.  With ``False`` (the default) a deterministic sample is used
        to keep the solver responsive for longer pins.

    The returned guess favours codes that are still viable candidates and breaks
    ties lexicographically for deterministic behaviour.
    """

    if len(candidates) == 1:
        return candidates[0]

    # Evaluate all possible guesses when requested or when the space is modest;
    # otherwise take a deterministic sample from both the candidate set and the
    # wider universe.  The sampling keeps larger games tractable while the
    # exhaustive mode can be used for research or to guarantee the minimal
    # number of guesses at the cost of speed.
    threshold = float("inf") if optimal else 2_000_000
    if len(candidates) * len(universe) <= threshold:
        pool = list(universe)
    else:
        sample_size = 100
        step = max(1, len(candidates) // sample_size)
        candidate_pool = list(candidates)[::step][:sample_size]
        other_pool: List[str] = []
        for code in universe:
            if code not in candidates:
                other_pool.append(code)
            if len(other_pool) >= sample_size:
                break
        pool = candidate_pool + other_pool

    best_guess = pool[0]
    best_score = float("inf")
    best_is_candidate = best_guess in candidates

    for guess in pool:
        partitions = Counter()
        for secret in candidates:
            partitions[compute_feedback(secret, guess)] += 1
        score = max(partitions.values())
        is_candidate = guess in candidates
        if (
            score < best_score
            or (score == best_score and is_candidate and not best_is_candidate)
            or (
                score == best_score
                and is_candidate == best_is_candidate
                and guess < best_guess
            )
        ):
            best_score = score
            best_guess = guess
            best_is_candidate = is_candidate

    return best_guess


def solve(
    length: int,
    feedback_func: Callable[[str], Tuple[int, int, int]],
    return_guess: bool = False,
    *,
    optimal: bool = False,
):
    """Solve the pin using the supplied feedback provider.

    Args:
        length: length of the pin being solved.
        feedback_func: callable receiving a guess string and returning a
            feedback tuple ``(correct_position, correct_wrong_place, incorrect)``.
        return_guess: if True, also return the final pin that was guessed.
        optimal: when True, always evaluate the entire search space to select
            the next guess.  This can drastically increase computation time but
            mirrors the strategy that guarantees four guesses for a four-digit
            PIN.

    Returns:
        The number of attempts it took to deduce the pin.  If ``return_guess`` is
        True the guessed pin is returned as a second value.
    """
    all_codes = generate_candidates(length)
    candidates = list(all_codes)
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
        guess = select_next_guess(candidates, all_codes, optimal=optimal)


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
    mode = input("Use slow optimal search? [y/N]: ").strip().lower()
    optimal = mode.startswith("y")
    attempts, guess = solve(
        length, provider, return_guess=True, optimal=optimal
    )
    print(f"\nSecret pin {guess} cracked in {attempts} attempts!")


# When executed as a script run the interactive version of the game.
if __name__ == "__main__":
    play()
    assert attempts > 0


def test_five_digit_random_pin():
    secret = "53124"
    attempts, guess = crack(secret)
    assert guess == secret
    assert attempts > 0


if __name__ == "__main__":  # pragma: no cover - manual demonstration
# Use a supplied secret from the command line or generate a random 4 digit one
    if len(sys.argv) > 1:
        secret_pin = sys.argv[1]
    else:
        secret_pin = "".join(str(random.randrange(10)) for _ in range(4))
    tries, found = crack(secret_pin)
    print(f"Secret pin {secret_pin} cracked as {found} in {tries} attempts")