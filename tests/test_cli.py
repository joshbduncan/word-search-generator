import random
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


@pytest.mark.skip(reason="update to match new rich output")
def test_random_secret_words_valid_input():
    output = subprocess.check_output("word-search -rx 5", shell=True)
    assert "Find these words: <ALL SECRET WORDS>" in str(output)


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


@pytest.mark.skip(reason="update to match new rich output")
def test_cli_output(iterations, builtin_mask_shapes):
    def parse_puzzle(output):
        return [[r[i] for i in range(0, len(r), 2)] for r in output.split("\n")[3:-6]]

    def parse_words(output):
        words = set()
        for w in output.split("\n")[-2:-1][0].split(": ")[1].split("), "):
            data = w.replace("(", "").replace(")", "").replace(",", "").split()
            text = data[0][1:] if "*" in data[0] else data[0]
            secret = bool("*" in data[0])
            word = Word(text, secret=secret)
            word.direction = Direction[data[1]]
            word.start_row = int(data[4]) - 1
            word.start_column = int(data[3]) - 1
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

    results = []
    for _ in range(iterations):
        size = random.randint(18, 36)
        words = random.randint(5, 21)
        mask = random.choice(builtin_mask_shapes)
        command = f"word-search -r {words} -s {size}"
        if mask:
            command += f" -m {mask.__class__.__name__}"
        output = subprocess.check_output(command, shell=True, text=True)
        puzzle = parse_puzzle(output)
        words = parse_words(output)
        results.append(all(check_chars(puzzle, word) for word in words))  # type: ignore

    assert all(results)


@pytest.mark.skip(reason="update to match new rich output")
def test_cli_output_lowercase(iterations, builtin_mask_shapes):
    def parse_puzzle(output):
        return [[r[i] for i in range(0, len(r), 2)] for r in output.split("\n")[3:-6]]

    def parse_words(output):
        words = set()
        for w in output.split("\n")[-2:-1][0].split(": ")[1].split("), "):
            data = w.replace("(", "").replace(")", "").replace(",", "").split()
            text = data[0][1:] if "*" in data[0] else data[0]
            words.add(text)
        return words

    def check_chars(puzzle, word):
        row, col = word.position
        for c in word.text:
            if c != puzzle[row][col]:
                return False
            row += word.direction.r_move
            col += word.direction.c_move
        return True

    for _ in range(iterations):
        size = random.randint(18, 36)
        words = random.randint(5, 21)
        mask = random.choice(builtin_mask_shapes)
        command = f"word-search -r {words} -s {size} -lc"
        if mask:
            command += f" -m {mask.__class__.__name__}"
        output = subprocess.check_output(command, shell=True, text=True)
        parsed_puzzle = parse_puzzle(output)
        parsed_words = parse_words(output)
        assert all("".join(row).islower() for row in parsed_puzzle)
        assert all(word.islower() for word in parsed_words)


def test_input_file(tmp_path: Path):
    file_to_read = Path.joinpath(tmp_path, "words.txt")
    file_to_read.write_text("dog, pig\nmoose,horse,cat,    mouse, newt\ngoose")
    result = subprocess.run(f"word-search -i {file_to_read.absolute()}", shell=True)
    assert result.returncode == 0


def test_no_sort_words():
    """Test that --no-sort-words preserves the original word order."""
    words = "hello world test"
    result = subprocess.run(
        f"word-search {words} --no-sort-words",
        shell=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # find the line with the word list
    for line in result.stdout.splitlines():
        if line.startswith("Word List:"):
            # extract the words from the line
            found_words = line.replace("Word List: ", "").split(", ")
            assert found_words == words.split()
            break


