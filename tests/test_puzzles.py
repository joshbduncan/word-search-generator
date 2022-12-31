import random
import subprocess
import uuid
from pathlib import Path

from pypdf import PdfReader

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

PUZZLES_TO_TEST = 5


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
    for _ in range(PUZZLES_TO_TEST):
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
    for _ in range(PUZZLES_TO_TEST):
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


def test_pdf_output_key(tmp_path):
    def parse_puzzle(extraction):
        puzzle = []
        for line in extraction.split("\n"):
            if line.startswith("WORD SEARCH"):
                continue
            elif line.startswith("Find words going"):
                break
            else:
                puzzle.append([c for c in line])
        return puzzle

    def parse_words(extraction):
        words = set()
        for w in extraction.replace("\n", " ").split(": ")[1].split("), "):
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
    for _ in range(PUZZLES_TO_TEST):
        p = WordSearch(size=random.randint(8, 21))
        p.random_words(random.randint(5, 21))
        path = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
        p.save(path)
        reader = PdfReader(path)
        page = reader.pages[0]
        puzzle = parse_puzzle(page.extract_text(0))
        words = parse_words(page.extract_text(180))
        print(puzzle)
        print(words)
        results.append(all(check_chars(puzzle, word) for word in words))  # type: ignore

    assert all(results)


def test_pdf_output_words(tmp_path):
    def parse_word_list(extraction):
        return set(
            word.strip()
            for word in "".join(
                extraction.split("Find words ")[1].split("\n")[1:]
            ).split(",")
        )

    def parse_words(extraction):
        words = set()
        for w in extraction.replace("\n", " ").split(": ")[1].split("), "):
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
    for i in range(PUZZLES_TO_TEST):
        p = WordSearch(size=random.randint(8, 21))
        p.random_words(random.randint(5, 21))
        path = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
        p.save(path)
        reader = PdfReader(path)
        page = reader.pages[0]
        word_list = parse_word_list(page.extract_text(0))
        words = parse_words(page.extract_text(180))
        for word in words:
            if word.secret:
                results.append(word.text not in word_list)
            else:
                results.append(word.text in word_list)

    assert all(results)
