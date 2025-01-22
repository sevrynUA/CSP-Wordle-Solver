# Wordle Solver and Bot
#
# This program simulates the game Wordle, an imperfect information game which is a constraint satisfaction problem. 
# Players have to guess a 5-letter word within 6 attempts, receiving feedback on the correctness of each letter.
# The feedback consists of 'G' (correct letter and position), 'Y' (correct letter but wrong position), and 'B' (incorrect letter).
# The bot uses a grid to track possible letters for each position in the word, applying constraints based on feedback. 
# It ranks words by summing letter frequency scores based on a predefined cryptography letter distribution.

import numpy as np
import pandas as pd
import random
import time
from collections import Counter
from typing import List, Dict, Set, Optional

# Cryptography Letter Frequency Distribution
LETTER_DISTRIBUTION = {
    'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2, 'G': 2.0, 'H': 6.1,
    'I': 7.0, 'J': 0.2, 'K': 0.8, 'L': 4.0, 'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9,
    'Q': 0.1, 'R': 6.0, 'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.2,
    'Y': 2.0, 'Z': 0.1
}

class Grid:
    def __init__(self, word: Optional[str] = None) -> None:
        """
        Initialize the Grid object with default constraints and the word dataset.

        Args:
            word (Optional[str]): The target word for the game. If None, a random word from the dataset is selected.
        """
        self._complete_domain: Set[str] = set("abcdefghijklmnopqrstuvwxyz")
        self._width: int = 5
        self._cells: List[Set[str]] = [self._complete_domain.copy() for _ in range(self._width)]

        # Letter count constraints
        self.letter_min_count: Counter[str] = Counter()  # minimum occurrences required
        self.letter_max_count: Counter[str] = Counter({char: 5 for char in self._complete_domain})  # maximum occurrences allowed

        # Read dataset
        df = pd.read_csv("data/possible_words.txt", header=None)
        words_list: List[str] = [str(w).strip() for w in df[0].values]
        self.allowed_words: np.ndarray = np.array(words_list, dtype=str)

        if word is not None:
            self.word: str = word
        else:
            self.word: str = random.choice(self.allowed_words)

    def get_cells(self) -> List[Set[str]]:
        """
        Get the current state of the grid cells.

        Returns:
            List[Set[str]]: A list of sets representing the possible letters for each position.
        """
        return self._cells

    def print_domains(self) -> None:
        """
        Print the current domains of each position in the grid, along with letter count constraints.
        """
        for i, domain in enumerate(self._cells):
            print(f"Position {i+1}: {sorted(domain)}")
        if self.letter_min_count:
            print("Minimum required occurrences:", dict(self.letter_min_count))
        if self.letter_max_count:
            print("Maximum allowed occurrences:", {k: v for k, v in self.letter_max_count.items() if v < 5})

    def is_solved(self) -> bool:
        """
        Check if the grid is solved (all positions have exactly one letter).

        Returns:
            bool: True if the grid is solved, False otherwise.
        """
        return all(len(cell) == 1 for cell in self._cells)

    def feedback(self, guess: str) -> str:
        """
        Generate feedback for a guess word against the target word.

        Args:
            guess (str): The guessed word.

        Returns:
            str: Feedback string composed of 'G', 'Y', and 'B' representing Green, Yellow, and Black.
        """
        feedback: List[str] = [""] * self._width
        used_positions: List[bool] = [False] * self._width

        # Greens
        for i in range(self._width):
            if guess[i] == self.word[i]:
                feedback[i] = 'G'
                used_positions[i] = True

        # Yellows and Blacks
        for i in range(self._width):
            if feedback[i] == "":
                letter: str = guess[i]
                placed: bool = False
                for j in range(self._width):
                    if self.word[j] == letter and not used_positions[j]:
                        feedback[i] = 'Y'
                        used_positions[j] = True
                        placed = True
                        break
                if not placed:
                    feedback[i] = 'B'

        return "".join(feedback)

    def propagate_constraints(self, guess: str, feedback: str) -> None:
        """
        Update the grid constraints based on the guess and feedback.

        Args:
            guess (str): The guessed word.
            feedback (str): Feedback string of 'G', 'Y', 'B' characters.
        """
        guess_letter_count: Counter[str] = Counter(guess)
        green_yellow_count: Counter[str] = Counter()

        # First, record greens and yellows to update min counts
        for fb, ch in zip(feedback, guess):
            if fb == 'G' or fb == 'Y':
                green_yellow_count[ch] += 1

        # Update minimum count of letters that appear as green or yellow
        for ch, cnt in green_yellow_count.items():
            if cnt > self.letter_min_count[ch]:
                self.letter_min_count[ch] = cnt

        # Handle Greens: Fix letter in that position
        for i, (char, fb) in enumerate(zip(guess, feedback)):
            if fb == 'G':
                self._cells[i] = {char}

        # Handle Yellows: Letter is in the word but not in this position
        for i, (char, fb) in enumerate(zip(guess, feedback)):
            if fb == 'Y':
                if char in self._cells[i]:
                    self._cells[i].discard(char)

        # Handle Blacks: The letter is not in the word at this frequency.
        for i, (char, fb) in enumerate(zip(guess, feedback)):
            if fb == 'B':
                if green_yellow_count[char] < guess_letter_count[char]:
                    self.letter_max_count[char] = min(self.letter_max_count[char], green_yellow_count[char])
                    for pos in range(self._width):
                        if len(self._cells[pos]) > 1:
                            self._cells[pos].discard(char)

    def prune_words(self) -> None:
        """
        Prune the list of allowed words based on current grid constraints.
        """
        possible_words: List[str] = []
        for word in self.allowed_words:
            valid: bool = True

            # Check positional domains
            for i, domain in enumerate(self._cells):
                if word[i] not in domain:
                    valid = False
                    break

            # Check letter min/max counts
            if valid:
                word_letter_count: Counter[str] = Counter(word)

                for ch, cnt in self.letter_min_count.items():
                    if word_letter_count[ch] < cnt:
                        valid = False
                        break

                if valid:
                    for ch, mx in self.letter_max_count.items():
                        if word_letter_count[ch] > mx:
                            valid = False
                            break

            if valid:
                possible_words.append(word)
        self.allowed_words = np.array(possible_words)

class WordleBot:
    def __init__(self, target_word: Optional[str] = None) -> None:
        """
        Initialize the WordleBot with a target word and associated grid.

        Args:
            target_word (Optional[str]): The target word for the game. Defaults to None.
        """
        self.grid: Grid = Grid(word=target_word)

    def rank_guess(self, word: str) -> float:
        """
        Rank a guess based on predefined letter frequencies.

        Args:
            word (str): The guessed word.

        Returns:
            float: The score of the guessed word based on letter frequencies.
        """
        return sum(LETTER_DISTRIBUTION.get(c.upper(), 0) for c in set(word))

    def play(self) -> int:
        """
        Simulate the Wordle game until the solution is found or attempts are exhausted.

        Returns:
            int: The number of attempts used to solve the word (or 7 if failed).
        """
        print(f"Wordle game started. Target word is: {self.grid.word}\n")
        max_attempts: int = 6
        attempts: int = 0

        while attempts < max_attempts:
            print("\nCurrent Grid State:")
            self.grid.print_domains()

            if self.grid.is_solved():
                solved_word: str = ''.join(list(cell)[0] for cell in self.grid.get_cells())
                print(f"Solved! The word is {solved_word} in {attempts} guesses.")
                return attempts

            if len(self.grid.allowed_words) == 0:
                print("No possible words remain. The game has failed.")
                return 7

            if attempts == 0:
                guess: str = "salet"
            else:
                guess = max(self.grid.allowed_words, key=self.rank_guess)

            print(f"Bot's guess: {guess}")

            feedback: str = self.grid.feedback(guess)
            print(f"Feedback: {feedback}")

            attempts += 1

            if feedback == "GGGGG":
                print(f"Solved! The word is {guess} in {attempts} guesses.")
                return attempts

            self.grid.propagate_constraints(guess, feedback)
            self.grid.prune_words()

        print(f"Game over! The bot failed to guess the word {self.grid.word} in {max_attempts} attempts.")
        return 7
    
def solve_all_words() -> None:
    """
    Solve all words in the dataset and provide statistics.
    """
    df = pd.read_csv("data/possible_words.txt", header=None, dtype=str)
    all_words: np.ndarray = df[0].values

    total_words: int = 0
    total_solved: int = 0
    total_failed: int = 0
    total_time: float = 0.0
    total_guesses: int = 0

    for w in all_words:
        total_words += 1
        start: float = time.time()
        bot: WordleBot = WordleBot(target_word=w)
        guesses: int = bot.play()
        end: float = time.time()
        elapsed: float = end - start
        total_time += elapsed

        total_guesses += guesses
        if guesses <= 6:
            total_solved += 1
        else:
            total_failed += 1

    avg_time: float = total_time / total_words if total_words > 0 else 0.0
    avg_guesses: float = total_guesses / total_words if total_words > 0 else 0.0

    print("\nSummary:")
    print("---------")
    print(f"Total Words: {total_words}")
    print(f"Total Solved: {total_solved}")
    print(f"Total Failed: {total_failed}")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Time: {avg_time:.2f} seconds per word")
    print(f"Average Guesses: {avg_guesses:.2f}")

def solve_word(word: str) -> None:
    """
    Solve a specific word using WordleBot.

    Args:
        word (str): The word to solve.
    """
    bot: WordleBot = WordleBot(target_word=word)
    bot.play()

def main() -> None:
    """
    Main
    """
    solve_all_words()

if __name__ == "__main__":
    main()
