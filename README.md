
# PIN Cracker Game

This is a Python-based PIN cracking game where the goal is for the program to guess a secret PIN. The user provides feedback after each guess, and the program uses this feedback to narrow down the possibilities and find the correct PIN.

## Features
- Generates all possible PIN combinations for a given length.
- Makes guesses based on feedback provided by the user.
- Uses an optimization algorithm to minimize the number of guesses.
- The user provides feedback in the format `(correct_position, correct_wrong_place, incorrect)`.
- The game uses an interactive interface where the user gives feedback after each guess.

## How It Works
1. The program generates all possible PIN combinations.
2. It makes an initial guess (e.g., `0123` for a 4-digit PIN).
3. The user provides feedback for each guess, which tells the program:
   - **Correct position**: How many digits are correct and in the correct position.
   - **Correct but wrong position**: How many digits are correct but in the wrong position.
   - **Incorrect**: How many digits are completely incorrect.
4. The program filters the list of candidates based on feedback and selects the next guess.
5. The process repeats until the correct PIN is found.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pin-cracker.git
   ```

2. Navigate to the project directory:
   ```bash
   cd pin-cracker
   ```

## Usage

To play the game interactively, run the following:

```bash
python pin_cracker.py
```

You will be prompted to enter the length of the PIN and give feedback for each guess in the format:
- `correct_position correct_wrong_place [incorrect]`
  
Example:
- `2 1 1` means 2 digits are in the correct position, 1 is correct but in the wrong position, and 1 is incorrect.

To quit the game, type `q` or `exit` when prompted for feedback.

## Game Example

### Steps:
1. **Enter PIN length**: `4`
2. **Program's guess**: `0123`
3. **Feedback format**: `2 1 1` (2 digits correct in the correct position, 1 correct but wrong position, and 1 incorrect)
4. Program continues guessing and narrowing down possibilities based on feedback.

### Output Example:
```
PIN Cracker - think of a secret PIN and I'll try to guess it!
Enter pin length: 4
Attempt 1: my guess is 0123
Enter feedback as 'correct_pos correct_wrong [incorrect]' (e.g. '2 1' or '2 1 1'), or 'q' to quit:
 > 2 1 1
Attempt 2: my guess is 1234
...
Secret pin 1234 cracked in 5 attempts!
```

## How the Algorithm Works
The program uses a **constraint satisfaction approach** to filter out possible candidates based on the feedback it receives. It then chooses the next guess based on minimizing the number of remaining possible candidates, using an optimization strategy to reduce the search space as efficiently as possible.

### Key Functions:
- **`generate_candidates(length: int)`**: Generates all possible PIN combinations for the given length.
- **`compute_feedback(secret: str, guess: str)`**: Computes feedback based on how the guess compares to the secret PIN.
- **`filter_candidates(candidates: Iterable[str], guess: str, feedback: Tuple[int, int, int])`**: Filters out candidates that do not match the feedback.
- **`select_next_guess(candidates: List[str])`**: Chooses the next guess based on minimizing the expected number of remaining candidates.
- **`solve(length: int, feedback_func: Callable[[str], Tuple[int, int, int]], return_guess: bool = False)`**: Main solving function that repeatedly guesses and refines the candidate list.
- **`interactive_feedback_factory(length: int)`**: Creates a feedback provider that interacts with the user.
- **`play()`**: Starts the interactive game, asking the user to think of a secret PIN and providing feedback after each guess.

## Contributing

Feel free to fork the repository and submit pull requests for improvements. Issues and suggestions are also welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
