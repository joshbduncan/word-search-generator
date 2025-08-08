import random
import re
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from word_search_generator.core.word import Direction, Word


def test_entrypoint():
    result = subprocess.run("word-search --help", shell=True)
    assert result.returncode == 0


def test_just_words():
    result = subprocess.run("word-search some test words", shell=True)
    assert result.returncode == 0


def test_with_secret_words():
    result = subprocess.run("word-search -r 10 -x fhqwhgads,dewlap", shell=True)
    assert result.returncode == 0


def test_stdin():
    result = subprocess.run("echo computer robot soda | word-search", shell=True)
    assert result.returncode == 0


def test_export_pdf(tmp_path: Path):
    fp = tmp_path.joinpath("test.pdf")
    result = subprocess.run(f'word-search some test words -o "{fp}"', shell=True)
    assert result.returncode == 0 and tmp_path.exists()


def test_export_csv(tmp_path: Path):
    fp = tmp_path.joinpath("test.csv")
    result = subprocess.run(f'word-search some test words -o "{fp}"', shell=True)
    assert result.returncode == 0 and tmp_path.exists()


def test_random_words_valid_input():
    result = subprocess.run("word-search -r 20", shell=True)
    assert result.returncode == 0


def test_random_words_invalid_input():
    result = subprocess.run("word-search -r 1000", shell=True)
    assert result.returncode == 2


def test_size_valid_input():
    result = subprocess.run("word-search some test words -s 20", shell=True)
    assert result.returncode == 0


def test_size_invalid_input():
    result = subprocess.run("word-search some test words -s 100", shell=True)
    assert result.returncode == 2


def test_dunder_main_entry_point():
    result = subprocess.run(
        "python -m word_search_generator.__main__ some test words", shell=True
    )
    assert result.returncode == 0


def test_cli_import_entry_point():
    result = subprocess.run(
        "python -m word_search_generator.cli some test words", shell=True
    )
    assert result.returncode == 0


def test_no_words_provided():
    result = subprocess.run("word-search -l 2", shell=True)
    assert result.returncode == 1


def test_level_difficulty_argument():
    result = subprocess.run("word-search -r 5 -l 2", shell=True)
    assert result.returncode == 0


def test_custom_difficulty_argument():
    result = subprocess.run("word-search -r 5 -d N,W", shell=True)
    assert result.returncode == 0


def test_invalid_difficulty_argument():
    result = subprocess.run("word-search -r 5 -d NNW", shell=True)
    assert result.returncode == 1


def test_invalid_argparse_difficulty_argument():
    result = subprocess.run("word-search -r 5 -d 1,N", shell=True)
    assert result.returncode == 2


def test_custom_difficulty_level_as_string():
    result = subprocess.run("word-search -r 5 -d 3", shell=True)
    assert result.returncode == 0


def test_random_words_mutual_exclusivity():
    result = subprocess.run("word-search dog pig cat -r 5", shell=True)
    assert result.returncode == 2


def test_random_secret_words_mutual_exclusivity():
    result = subprocess.run("word-search dog pig cat -rx 5 -x 'cow ant'", shell=True)
    assert result.returncode == 2


def test_random_secret_words_invalid_input():
    result = subprocess.run("word-search -rx 500", shell=True)
    assert result.returncode == 2


def test_preview_masks():
    result = subprocess.run("word-search -pm", shell=True)
    assert result.returncode == 0


def test_mask():
    result = subprocess.run("word-search -r 5 -s 21 -m Triangle", shell=True)
    assert result.returncode == 0


def test_shape_mask_min_size():
    result = subprocess.run("word-search -r 1 -m Club", shell=True)
    assert result.returncode == 0


def test_invalid_mask():
    result = subprocess.run("word-search -r 5 -s 21 -m Heptakaideka", shell=True)
    assert result.returncode == 2


def test_image_mask(tmp_path: Path):
    name = "test_image.jpg"
    test_img = Image.new("L", (100, 100), (0))
    img_path = Path.joinpath(tmp_path, name)
    test_img.save(img_path, "JPEG")
    result = subprocess.run(f"word-search -r 5 -im {img_path}", shell=True)
    assert result.returncode == 0


@pytest.mark.repeat(10)
def test_cli_output(builtin_mask_shapes):
    def parse_puzzle(output):
        return [[r[i] for i in range(0, len(r), 2)] for r in output.split("\n")[3:-6]]

    def parse_words(output):
        words = set()
        words_line = output.split("\n")[-1].split(": ")[-1]
        pattern = r"(\*?)(\w+)\s+(\w+)\s+@\s+\((\d+),\s*(\d+)\)"
        matches = re.findall(pattern, words_line)

        for secret, w, d, col, row in matches:
            # reverse word back to original
            w = w[::-1]

            # convert coords and offset
            row = int(row) - 1
            col = int(col) - 1

            word = Word(w, secret=secret == "*")
            word.direction = Direction[d]
            word.start_row = row
            word.start_column = col
            words.add(word)
        return words

    def check_chars(puzzle, word):
        row, col = word.position
        for c in word.text:
            if c != puzzle[row][col]:
                return False
            row += word.direction.r_move
            col += word.direction.c_move
        return True

    size = random.randint(18, 36)
    words = random.randint(5, 21)
    mask = random.choice(builtin_mask_shapes)
    command = f"word-search -r {words} -s {size}"
    if mask:
        command += f" -m {mask.__class__.__name__}"
    output = subprocess.check_output(command, shell=True, text=True)
    # assert output == ""
    puzzle = parse_puzzle(output)
    words = parse_words(output)
    assert all(check_chars(puzzle, word) for word in words)  # type: ignore


@pytest.mark.repeat(10)
def test_cli_output_lowercase(builtin_mask_shapes):
    def parse_words(output):
        words = set()
        words_line = output.split("\n")[-1].split(": ")[-1]
        pattern = r"(\*?)(\w+)\s+(\w+)\s+@\s+\((\d+),\s*(\d+)\)"
        matches = re.findall(pattern, words_line)

        for secret, w, d, col, row in matches:
            # reverse word back to original
            w = w[::-1]

            # convert coords and offset
            row = int(row) - 1
            col = int(col) - 1

            word = Word(w, secret=secret == "*")
            word.direction = Direction[d]
            word.start_row = row
            word.start_column = col
            words.add(word)
        return words

    size = random.randint(18, 36)
    words = random.randint(5, 21)
    mask = random.choice(builtin_mask_shapes)
    command = f"word-search -r {words} -s {size} -lc"
    if mask:
        command += f" -m {mask.__class__.__name__}"
    output = subprocess.check_output(command, shell=True, text=True)
    parsed_puzzle = output.split("\n")
    assert all("".join(row).islower() for row in parsed_puzzle[2:5])
    parsed_words = parse_words(output)
    assert all(word.islower() for word in parsed_words)


def test_input_file(tmp_path: Path):
    file_to_read = Path.joinpath(tmp_path, "words.txt")
    file_to_read.write_text("dog, pig\nmoose,horse,cat,    mouse, newt\ngoose")
    result = subprocess.run(f"word-search -i {file_to_read.absolute()}", shell=True)
    assert result.returncode == 0


def test_no_sort_words_cli_flag():
    """Test that --no-sort-words CLI flag works."""
    # Test with non-alphabetical words
    result = subprocess.run(
        'word-search "zebra, apple, cat" --no-sort-words',
        shell=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout

    # Check that words appear in original order, not alphabetical
    lines = output.split("\n")
    word_line = None
    for line in lines:
        if "ZEBRA" in line and "APPLE" in line and "CAT" in line:
            word_line = line
            break

    assert word_line is not None
    # Should be "ZEBRA, APPLE, CAT" not "APPLE, CAT, ZEBRA"
    zebra_pos = word_line.find("ZEBRA")
    apple_pos = word_line.find("APPLE")
    cat_pos = word_line.find("CAT")

    assert zebra_pos < apple_pos < cat_pos


def test_default_sorted_words_cli():
    """Test that default behavior sorts words alphabetically."""
    result = subprocess.run(
        'word-search "zebra, apple, cat"', shell=True, capture_output=True, text=True
    )
    assert result.returncode == 0
    output = result.stdout

    # Check that words appear in alphabetical order
    lines = output.split("\n")
    word_line = None
    for line in lines:
        if "ZEBRA" in line and "APPLE" in line and "CAT" in line:
            word_line = line
            break

    assert word_line is not None
    # Should be "APPLE, CAT, ZEBRA" not "ZEBRA, APPLE, CAT"
    apple_pos = word_line.find("APPLE")
    cat_pos = word_line.find("CAT")
    zebra_pos = word_line.find("ZEBRA")

    assert apple_pos < cat_pos < zebra_pos


def test_no_sort_words_with_output_formats(tmp_path: Path):
    """Test --no-sort-words works with different output formats."""
    # Test CSV output
    csv_file = tmp_path / "test.csv"
    result = subprocess.run(
        f'word-search "zebra, apple, cat" --no-sort-words -o {csv_file} -f CSV',
        shell=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert csv_file.exists()

    # Read CSV and check word order
    csv_content = csv_file.read_text()
    lines = csv_content.split("\n")
    word_list_line = None
    for line in lines:
        if "ZEBRA" in line and "APPLE" in line:
            word_list_line = line
            break

    assert word_list_line is not None
    # Should maintain original order in CSV
    zebra_pos = word_list_line.find("ZEBRA")
    apple_pos = word_list_line.find("APPLE")
    assert zebra_pos < apple_pos

    # Test JSON output
    json_file = tmp_path / "test.json"
    result = subprocess.run(
        f'word-search "dog, cat, bat" --no-sort-words -o {json_file} -f JSON',
        shell=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json_file.exists()

    import json

    with open(json_file) as f:
        data = json.load(f)

    # Check that words list maintains original order
    words = data.get("words", [])
    assert len(words) >= 3
    # Original order should be preserved in some way in the output
