import pathlib
import subprocess


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


def test_export_pdf(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    result = subprocess.run(f"word-search some test words -o {tmp_path}", shell=True)
    assert result.returncode == 0 and tmp_path.exists()


def test_export_csv(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    result = subprocess.run(f"word-search some test words -o {tmp_path}", shell=True)
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


def test_random_secret_words_valid_input(capsys):
    output = subprocess.check_output("word-search -rx 5", shell=True)
    assert "Find these words: <ALL SECRET WORDS>" in str(output)


def test_random_secret_words_invalid_input():
    result = subprocess.run("word-search -rx 500", shell=True)
    assert result.returncode == 2
