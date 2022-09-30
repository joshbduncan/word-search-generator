import pathlib
import subprocess

test_words = "some test words"


def test_entrypoint():
    result = subprocess.run(
        ["word-search", "--help"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0


def test_no_words_provided():
    result = subprocess.run(
        ["word-search"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 1


def test_just_words():
    result = subprocess.run(["word-search", test_words])
    print(result)
    assert result.returncode == 0


def test_stdin():
    result = subprocess.run(
        ["echo", test_words, "word-search"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0


def test_export_pdf(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    result = subprocess.run(
        ["word-search", test_words, "-o", tmp_path],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0 and tmp_path.exists()


def test_export_csv(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    result = subprocess.run(
        ["word-search", test_words, "-o", tmp_path],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0 and tmp_path.exists()


def test_random_word_valid_input():
    result = subprocess.run(
        ["word-search", "-r", "20"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0


def test_random_word_invalid_input():
    result = subprocess.run(
        ["word-search", "-r", "100"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 2


def test_size_valid_input():
    result = subprocess.run(
        ["word-search", test_words, "-s", "20"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0


def test_size_invalid_input():
    result = subprocess.run(
        ["word-search", test_words, "-s", "100"],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 2


def test_dunder_main_entry_point():
    result = subprocess.run(
        ["python", "-m", "word_search_generator.__main__", test_words],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0


def test_cli_import_entry_point():
    result = subprocess.run(
        ["python", "-m", "word_search_generator", test_words],
        stdout=subprocess.DEVNULL,
    )
    assert result.returncode == 0
