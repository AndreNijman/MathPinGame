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
    assert guess == "0194"
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