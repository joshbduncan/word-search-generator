import random
import subprocess

from word_search_generator import WordSearch
from word_search_generator.mask.shapes import (
    Circle,
    Diamond,
    Donut,
    Heart,
    Hexagon,
    Octagon,
    Pentagon,
    Star5,
    Star6,
    Star8,
    Tree,
    Triangle,
)
from word_search_generator.word import Direction, Word

MASKS = [
    None,
    Circle(),
    Diamond(),
    Donut(),
    Heart(),
    Hexagon(),
    Octagon(),
    Pentagon(),
    Star5(),
    Star6(),
    Star8(),
    Tree(),
    Triangle(),
]


def check_chars(puzzle, word):
    row, col = word.position
    for c in word.text:
        if c != puzzle[row][col]:
            return False
        row += word.direction.r_move
        col += word.direction.c_move
    return True


def test_word_placement():
    results = []
    for _ in range(10):
        p = WordSearch(size=random.randint(8, 21))
        p.random_words(random.randint(5, 21))
        mask = random.choice(MASKS)
        if mask:
            p.apply_mask(mask)
        results.append(all(check_chars(p.puzzle, word) for word in p.placed_words))

    assert all(results)


def test_cli_output():
    def parse_puzzle(output):
        return [[r[i] for i in range(0, len(r), 2)] for r in output.split("\n")[3:-6]]

    def parse_words(output):
        words = set()
        for w in output.split("\n")[-2:-1][0].split(": ")[1].split("), "):
            data = w.replace("(", "").replace(")", "").replace(",", "").split()
            text = data[0][1:] if "*" in data[0] else data[0]
            secret = True if "*" in data[0] else False
            word = Word(text, secret=secret)
            word.direction = Direction[data[1]]
            word.start_row = int(data[4]) - 1
            word.start_column = int(data[3]) - 1
            words.add(word)
        return words

    results = []
    for _ in range(5):
        size = random.randint(8, 21)
        words = random.randint(5, 21)
        mask = random.choice(MASKS)
        command = f"word-search -r {words} -s {size}"
        if mask:
            command += f" -m {mask.__class__.__name__}"
        output = subprocess.check_output(command, shell=True, text=True)
        puzzle = parse_puzzle(output)
        words = parse_words(output)
        results.append(all(check_chars(puzzle, word) for word in words))  # type: ignore

    assert all(results)
