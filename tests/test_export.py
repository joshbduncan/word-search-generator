import csv
import json
import math
import os
import random
import re
import uuid
from pathlib import Path
from typing import Any

import pdfplumber
import pytest
from pdfplumber.page import Page
from pypdf import PdfReader

from word_search_generator import WordSearch
from word_search_generator.core.formatter import ExportFormat
from word_search_generator.core.game import EmptyPuzzleError
from word_search_generator.core.word import Direction, Word
from word_search_generator.utils import get_random_words, get_word_list_list

# TODO: add alternation for lowercase in tests


def check_chars(puzzle, word) -> bool:
    row, col = word.position
    for c in word.text:
        if c != puzzle[row][col]:
            return False
        row += word.direction.r_move
        col += word.direction.c_move
    return True


def parse_csv_puzzle_file(
    fp: Path, puzzle_size
) -> tuple[list[list[str]], list[str], list[str], list[str]]:
    puzzle = []
    with open(fp) as f:
        data = [row for row in csv.reader(f)]  # noqa: C416

    # extract each part
    puzzle = data[1 : puzzle_size + 1]
    word_list = data[puzzle_size + 3]
    directions = [
        d[0] for d in re.findall(r"\s([A-Z]+)(,|\.)", data[puzzle_size + 4][0])
    ]
    answer_key = data[puzzle_size + 7]

    return (puzzle, word_list, directions, answer_key)


def lines_intersection(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x3: float,
    y3: float,
    x4: float,
    y4: float,
) -> bool:
    """Determine if two lines intersect.

    Args:
        x1: Line A point 1 x location.
        y1: Line A point 1 y location.
        x2: Line A point 2 x location.
        y2: Line A point 2 y location.
        x3: Line B point 1 x location.
        y3: Line B point 1 y location.
        x4: Line B point 2 x location.
        y4: Line B point 2 y location.

    Returns:
        Lines intersect.
    """
    # calculate line directions
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / (
        (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        or 1  # or 1 for zero division error
    )
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / (
        (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        or 1  # or 1 for zero division error
    )
    return ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1


def line_rect_intersect(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    rx: float,
    ry: float,
    rw: float,
    rh: float,
) -> bool:
    """Determine if a line intersects a rectangle (rectangle falls along line).

    Args:
        x1: Line point 1 x position.
        y1: Line point 1 y position.
        x2: Line point 2 x position.
        y2: Line point 2 y position.
        rx: Rectangle point 1 x position (top-left).
        ry: Rectangle point 1 y position (top-left).
        rw: Rectangle width.
        rh: Rectangle height.

    Returns:
        Line intersects rectangle.
    """
    left = lines_intersection(x1, y1, x2, y2, rx, ry, rx, ry - rh)
    right = lines_intersection(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry - rh)
    top = lines_intersection(x1, y1, x2, y2, rx, ry, rx + rw, ry)
    bottom = lines_intersection(x1, y1, x2, y2, rx, ry - rh, rx + rw, ry - rh)
    return any([left, right, top, bottom])


def rect_contains_line(
    lx1: float,
    ly1: float,
    lx2: float,
    ly2: float,
    rx1: float,
    ry1: float,
    rx2: float,
    ry2: float,
) -> bool:
    """Determine if a line is completely contained inside of a rectangle.

    Args:
        lx1: Line point 1 x position.
        ly1: Line point 1 y position.
        lx2: Line point 2 x position.
        ly2: Line point 2 y position.
        rx1: Rectangle point 1 x position.
        ry1: Rectangle point 1 y position.
        rx2: Rectangle point 2 x position.
        ry2: Rectangle point 2 y position.

    Returns:
        Line intersects rectangle.
    """
    return (
        min(rx1, rx2) <= min(lx1, lx2)
        and max(rx1, rx2) >= max(lx1, lx2)
        and min(ry1, ry2) <= min(ly1, ly2)
        and max(ry1, ry2) >= max(ly1, ly2)
    )


def extract_puzzle_highlight_lines(page: Page) -> list[list[float]]:
    lines: list[list[float]] = []
    for line in page.lines[: len(page.lines) // 2]:
        # ignore any non highlight lines
        pts: list[float] = []
        for pt in line["pts"]:
            x, y = pt
            y = page.height - y  # flip y for testing
            pts.extend([x, y])
        lines.append(pts)
    return lines


def extract_wordlist_highlight_lines(page: Page) -> list[list[float]]:
    lines: list[list[float]] = []
    for line in page.lines[len(page.lines) // 2 :]:
        lines.append([pt for line_pt in line["pts"] for pt in line_pt])
    return lines


def test_export_csv(words, tmp_path: Path):
    puzzle = WordSearch(words)
    fp = Path.joinpath(tmp_path, "test.csv")
    puzzle.save(fp, format=ExportFormat.CSV)
    (
        extracted_puzzle,
        extracted_words,
        extracted_directions,
        extracted_key,
    ) = parse_csv_puzzle_file(fp, puzzle.size)

    # extract start positions from key
    regex = re.compile(r"^(\w+).*?(\d+).*?(\d+)")
    key_info = [regex.findall(s)[0] for s in extracted_key]

    assert puzzle.puzzle == extracted_puzzle
    assert all(w.text in extracted_words for w in puzzle.placed_hidden_words)
    assert all(d.name in extracted_directions for d in puzzle.level)
    assert all(
        puzzle.puzzle[int(y) - 1][int(x) - 1] == word[0] for word, x, y in key_info
    )


def test_export_csv_only_secret_words(tmp_path: Path):
    puzzle = WordSearch(secret_words="cat bat rat hat")
    fp = Path.joinpath(tmp_path, "test.csv")
    puzzle.save(fp, format=ExportFormat.CSV)
    (
        extracted_puzzle,
        extracted_words,
        extracted_directions,
        extracted_key,
    ) = parse_csv_puzzle_file(fp, puzzle.size)

    # extract start positions from key
    regex = re.compile(r"(\w+).*?(\d+).*?(\d+)")
    key_info = [regex.findall(s)[0] for s in extracted_key]

    assert puzzle.puzzle == extracted_puzzle
    assert extracted_words[0] == "<ALL SECRET WORDS>"
    assert all(d.name in extracted_directions for d in puzzle.level)
    assert all(
        puzzle.puzzle[int(y) - 1][int(x) - 1] == word[0] for word, x, y in key_info
    )


def test_export_csv_lowercase(words, tmp_path: Path):
    puzzle = WordSearch(words)
    fp = Path.joinpath(tmp_path, "test.csv")
    puzzle.save(fp, format=ExportFormat.CSV, lowercase=True)
    (
        extracted_puzzle,
        extracted_words,
        extracted_directions,
        extracted_key,
    ) = parse_csv_puzzle_file(fp, puzzle.size)

    # extract start positions from key
    regex = re.compile(r"^(\w+).*?(\d+).*?(\d+)")
    key_info = [regex.findall(s)[0] for s in extracted_key]

    # convert puzzle to lowercase for testing
    lowercase_puzzle = [[c.lower() for c in line] for line in puzzle.puzzle]

    assert lowercase_puzzle == extracted_puzzle
    assert all(w.text.lower() in extracted_words for w in puzzle.placed_hidden_words)
    assert all(d.name in extracted_directions for d in puzzle.level)
    assert all(
        lowercase_puzzle[int(y) - 1][int(x) - 1] == word[0] for word, x, y in key_info
    )


def test_export_json(words, tmp_path: Path):
    puzzle = WordSearch(words)
    fp = Path.joinpath(tmp_path, "test.json")
    puzzle.save(fp, format=ExportFormat.JSON)
    data = json.loads(Path(fp).read_text())
    for word in puzzle.words:
        assert word.text in data["words"]


def test_export_json_lowercase(words, tmp_path: Path):
    puzzle = WordSearch(words)
    fp = Path.joinpath(tmp_path, "test.json")
    puzzle.save(fp, format=ExportFormat.JSON, lowercase=True)
    data = json.loads(Path(fp).read_text())
    for word in puzzle.words:
        assert word.text.lower() in data["words"]


@pytest.mark.parametrize(
    "format",
    [
        ("csv",),
        ("json",),
        ("pdf",),
    ],
)
def test_export_empty_puzzle(tmp_path: Path, format):
    puzzle = WordSearch()
    fp = Path.joinpath(tmp_path, f"test.{format}")
    with pytest.raises(EmptyPuzzleError):
        puzzle.save(fp, format=format)


@pytest.mark.repeat(10)
def test_export_pdf_puzzles(tmp_path: Path):
    """Export a bunch of puzzles as PDF and make sure they are all 1-page."""
    size = random.randint(WordSearch.MIN_PUZZLE_SIZE, WordSearch.MAX_PUZZLE_SIZE)
    words = get_random_words(
        random.randint(WordSearch.MIN_PUZZLE_WORDS, WordSearch.MAX_PUZZLE_WORDS)
    )
    shortest_word_length: int = len(min(words.split(","), key=len))
    if size < shortest_word_length:
        size = shortest_word_length
    level = random.randint(1, 3)
    puzzle = WordSearch(words, level=level, size=size)
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    puzzle.save(fp, format=ExportFormat.PDF)

    with open(fp, "rb") as f:
        pdf = PdfReader(f)
        assert len(pdf.pages) == 1


@pytest.mark.repeat(10)
def test_export_pdf_puzzle_with_solution(tmp_path: Path):
    """Make sure a pdf puzzle exported with the solution is 2 pages."""
    wordlist = get_random_words(
        random.randint(WordSearch.MIN_PUZZLE_WORDS, WordSearch.MAX_PUZZLE_WORDS)
    )
    shortest_word_length: int = len(min(wordlist.split(","), key=len))
    size = random.choice(
        range(
            max(WordSearch.MIN_PUZZLE_SIZE, shortest_word_length),
            WordSearch.MAX_PUZZLE_SIZE,
        )
    )
    level = random.randint(1, 3)
    puzzle = WordSearch(wordlist, level=level, size=size)
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    puzzle.save(fp, solution=True)
    pages = pdfplumber.open(fp).pages
    assert len(pages) == 2


def test_export_pdf_overwrite_file_error(tmp_path: Path):
    """Try to export a puzzle with the name of a file that is already present."""
    fp = Path.joinpath(tmp_path, "test_pdf.pdf")
    fp.touch()
    puzzle = WordSearch("cat, bird, donkey")
    with pytest.raises(FileExistsError):
        puzzle.save(fp)


def test_export_csv_overwrite_file_error(tmp_path: Path):
    """Try to export a puzzle with the name of a file that is already present."""
    fp = Path.joinpath(tmp_path, "test_csv.pdf")
    fp.touch()
    puzzle = WordSearch("cat, bird, donkey")
    with pytest.raises(FileExistsError):
        puzzle.save(fp, format=ExportFormat.CSV)


def test_export_json_overwrite_file_error(tmp_path: Path):
    """Try to export a puzzle with the name of a file that is already present."""
    fp = Path.joinpath(tmp_path, "test_json.pdf")
    fp.touch()
    puzzle = WordSearch("cat, bird, donkey")
    with pytest.raises(FileExistsError):
        puzzle.save(fp, format=ExportFormat.JSON)


def test_export_pdf_os_error(words):
    """Try to export a puzzle to a place you don't have access to, regardless of OS."""
    puzzle = WordSearch(words)

    # Pick a path that will trigger an OSError on each platform
    if os.name == "nt":  # Windows
        # "CON" is a reserved name in Windows and cannot be used as a filename
        forbidden_path = "CON\\test.pdf"
    else:  # posix (macOS, Linux)
        # Attempting to write directly to root or /sys should fail without root
        forbidden_path = "/this/should/not/exist/test.pdf"

    with pytest.raises(OSError):
        puzzle.save(forbidden_path)


def test_export_csv_os_error(words):
    """Try to export a puzzle to a place you don't have access to, regardless of OS."""
    puzzle = WordSearch(words)

    # Pick a path that will trigger an OSError on each platform
    if os.name == "nt":  # Windows
        # "CON" is a reserved name in Windows and cannot be used as a filename
        forbidden_path = "CON\\test.csv"
    else:  # posix (macOS, Linux)
        # Attempting to write directly to root or /sys should fail without root
        forbidden_path = "/this/should/not/exist/test.csv"

    with pytest.raises(OSError):
        puzzle.save(forbidden_path)


@pytest.mark.repeat(10)
def test_pdf_output_puzzle_lowercase(tmp_path: Path):
    def parse_puzzle(extraction):
        puzzle = []
        for line in extraction.split("\n"):
            if line.startswith("WORD SEARCH"):
                continue
            elif line.startswith("Find words going"):
                break
            else:
                puzzle.append(list(line.replace(" ", "")))
        return puzzle

    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp, lowercase=True)
    reader = PdfReader(fp)
    page = reader.pages[0]
    puzzle = parse_puzzle(page.extract_text(0))

    # convert puzzle to lowercase for testing
    lowercase_puzzle = [[c.lower() for c in line if c] for line in ws.puzzle]

    assert puzzle == lowercase_puzzle


@pytest.mark.repeat(10)
def test_pdf_output_key(tmp_path: Path):
    def parse_puzzle(extraction):
        puzzle = []
        for line in extraction.split("\n"):
            if line.startswith("WORD SEARCH"):
                continue
            elif line.startswith("Find words going"):
                break
            else:
                puzzle.append(list(line.replace(" ", "")))
        return puzzle

    def parse_words(extraction):
        words = set()
        for w in extraction.replace("\n", " ").split(": ")[1].split("), "):
            data = w.replace("(", "").replace(")", "").replace(",", "").split()
            text = data[0][1:] if "*" in data[0] else data[0]
            secret = bool("*" in data[0])
            word = Word(text, secret=secret)
            word.direction = Direction[data[1]]
            word.start_row = int(data[4]) - 1
            word.start_column = int(data[3]) - 1
            words.add(word)
        return words

    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp)
    reader = PdfReader(fp)
    page = reader.pages[0]
    puzzle = parse_puzzle(page.extract_text(0))
    words = parse_words(page.extract_text(180))
    assert all(check_chars(puzzle, word) for word in words)  # type: ignore


@pytest.mark.repeat(10)
def test_pdf_output_words(tmp_path: Path):
    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    lowercase = random.choice([True, False])
    ws.save(fp, lowercase=lowercase)

    # extract both pages
    pages = pdfplumber.open(fp).pages

    # extract wordlist
    placed_words = [word.text for word in ws.placed_words]

    # find where wordlist should start
    for i, page in enumerate(pages):
        start = 2 + ws.size**2  # "WORD SEARCH" == 2 then add puzzle size
        if i == 1:
            start += 1  # addition "(SOLUTION)" word
        extracted_words = page.extract_words()
        for i, word in enumerate(extracted_words[start:]):
            if ":" in word["text"]:
                start += i + 1
                break
        end = start + len(placed_words)
        extracted_wordlist = [
            word
            for word in extracted_words[start:end]
            if word["text"].upper() in placed_words
        ]
        assert len(ws.placed_words) == len(extracted_wordlist)


@pytest.mark.repeat(10)
def test_pdf_output_words_secret_only(tmp_path: Path):
    words = "cat bat rat hat mat"
    ws = WordSearch(secret_words=words, size=random.randint(8, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    lowercase = random.choice([True, False])
    ws.save(
        fp,
        solution=random.choice([True, False]),
        lowercase=lowercase,
    )

    pages = pdfplumber.open(fp).pages
    page1 = pages[0]
    assert "<ALL SECRET WORDS>" in "".join(c["text"] for c in page1.chars)
    if len(pages) == 2:
        page2 = pages[1]
        word_list = get_word_list_list(ws.words)
        word_list_as_strings = (
            [w.text.lower() for w in word_list]
            if lowercase
            else [w.text for w in word_list]
        )
        extracted_words = [
            word
            for word in page2.extract_words()
            if word["text"] in word_list_as_strings
        ]
        assert len(extracted_words) == len(ws.placed_hidden_words)


@pytest.mark.repeat(10)
def test_pdf_output_puzzle_size(tmp_path: Path):
    def parse_puzzle(extraction):
        puzzle = []
        for line in extraction.split("\n"):
            if line.startswith("WORD SEARCH"):
                continue
            elif line.startswith("Find words going"):
                break
            else:
                puzzle.append(list(line.replace(" ", "")))
        return puzzle

    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp)
    reader = PdfReader(fp)
    page = reader.pages[0]
    puzzle = parse_puzzle(page.extract_text(0))
    assert ws.size == len(puzzle)
    assert ws.size == len(puzzle[0])


@pytest.mark.repeat(10)
def test_pdf_output_solution_highlighting(tmp_path: Path):
    def validate_puzzle_highlighting(
        ws: WordSearch,
        puzzle: list[dict[str, Any]],
        lines: list[list[float]],
    ):
        for word in ws.placed_hidden_words:
            for y, x in word.coordinates:
                char = puzzle[y * ws.size + x]
                rx, ry, rw, rh = char["x0"], char["y1"], char["width"], char["height"]
                intersection = False
                for x1, y1, x2, y2 in lines:
                    if line_rect_intersect(x1, y1, x2, y2, rx, ry, rw, rh):
                        intersection = True
                        break
                assert intersection

    def validate_wordlist_highlighting(
        words: list[dict[str, Any]],
        lines: list[list[float]],
    ):
        for i, word in enumerate(words):
            lx1, ly1, lx2, ly2 = lines[i]
            rx1, ry1, rx2, ry2 = (
                word["x0"],
                word["top"],
                word["x1"],
                word["bottom"],
            )
            assert rect_contains_line(lx1, ly1, lx2, ly2, rx1, ry1, rx2, ry2)

    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp, format=ExportFormat.PDF, solution=True)

    # read solution page from PDF
    page = pdfplumber.open(fp).pages[1]
    assert page

    # extract puzzle line and wordlist lines
    puzzle_lines = extract_puzzle_highlight_lines(page)
    assert puzzle_lines
    assert len(puzzle_lines) == len(page.lines) // 2

    wordlist_lines = extract_wordlist_highlight_lines(page)
    assert wordlist_lines
    assert len(wordlist_lines) == len(page.lines) // 2

    # find positions of puzzle and wordlist characters
    chars_str = "".join(c["text"] for c in page.chars)
    title = re.search(r"WORD.*\(SOLUTION\)", chars_str)
    level_dirs = re.search(r"Find.*?:", chars_str)
    answer_key = re.search("Answer Key", chars_str)

    assert title and level_dirs and answer_key

    puzzle_start = title.end()
    puzzle_end = level_dirs.start()

    # extract puzzle
    extracted_puzzle = page.chars[puzzle_start:puzzle_end]
    assert ws.size == int(math.sqrt(len(extracted_puzzle)))

    # validate puzzle highlighting
    validate_puzzle_highlighting(ws, extracted_puzzle, puzzle_lines)

    # extract wordlist
    placed_words = [word.text for word in ws.placed_words]

    # find where wordlist should start
    start = 3 + ws.size**2  # "WORD SEARCH (SOLUTION)" == 3 then add puzzle size *
    extracted_words = page.extract_words()
    for i, word in enumerate(extracted_words[start:]):
        if ":" in word["text"]:
            start += i + 1
            break
    end = start + len(placed_words)
    extracted_wordlist = [
        word
        for word in extracted_words[start:end]
        if word["text"].upper() in placed_words
    ]
    assert len(ws.placed_words) == len(extracted_wordlist)

    # check all wordlist characters are highlighted
    validate_wordlist_highlighting(extracted_wordlist, wordlist_lines)


@pytest.mark.repeat(10)
def test_pdf_output_solution_character_placement(tmp_path: Path):
    # TODO: check for secret words too
    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp, format=ExportFormat.PDF, solution=True)

    # read solution page from PDF
    page = pdfplumber.open(fp).pages[1]
    assert page

    # split puzzle line and wordlist lines
    puzzle_lines = extract_puzzle_highlight_lines(page)
    assert puzzle_lines

    # find positions of puzzle and wordlist characters
    chars_str = "".join(c["text"] for c in page.chars)
    title = re.search(r"WORD.*\(SOLUTION\)", chars_str)
    level_dirs = re.search(r"Find.*?:", chars_str)

    assert title
    assert level_dirs

    puzzle_start = title.end()
    puzzle_end = level_dirs.start()

    # extract puzzle
    extracted_puzzle = page.chars[puzzle_start:puzzle_end]
    assert ws.size == int(math.sqrt(len(extracted_puzzle)))

    # check placement of all word characters
    for word in ws.placed_hidden_words:
        for i, coord in enumerate(word.coordinates):
            y, x = coord
            word_char = word.text[i]
            puzzle_char = extracted_puzzle[y * ws.size + x]["text"]
            assert word_char == puzzle_char


@pytest.mark.repeat(10)
def test_csv_output_puzzle_size(tmp_path: Path):
    def parse_puzzle(fp):
        puzzle = []
        with open(fp, newline="") as f:
            data = csv.reader(f)
            for i, row in enumerate(data):
                if i == 0:
                    continue
                elif row == [""]:
                    break
                else:
                    puzzle.append(row)
        return puzzle

    ws = WordSearch(size=random.randint(8, 21))
    ws.random_words(random.randint(5, 21))
    fp = Path.joinpath(tmp_path, f"{uuid.uuid4()}.pdf")
    ws.save(fp, format=ExportFormat.CSV)
    puzzle = parse_puzzle(fp)
    assert ws.size == len(puzzle)
    assert ws.size == len(puzzle[0])
