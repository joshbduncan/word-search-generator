import os
import pathlib
import tempfile

import pytest


@pytest.fixture()
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield pathlib.Path(temp_dir)


def get_exit_status(exit_code):
    if os.name == "nt":
        # On Windows, os.WEXITSTATUS() doesn't work and os.system() returns
        # the argument to exit() directly.
        return exit_code
    else:
        # On Unix, os.WEXITSTATUS() must be used to extract the exit status
        # from the result of os.system().
        if os.WIFEXITED(exit_code):
            return os.WEXITSTATUS(exit_code)
        else:
            return -1


def test_entrypoint():
    result = os.system("word-search --help")
    assert get_exit_status(result) == 0


def test_no_words_provided():
    result = os.system("word-search")
    assert get_exit_status(result) == 1


def test_just_words():
    result = os.system("word-search some test words")
    assert get_exit_status(result) == 0


def test_stdin():
    result = os.system("echo computer robot soda | word-search")
    assert get_exit_status(result) == 0


def test_export_pdf(temp_dir):
    temp_path = pathlib.Path.joinpath(temp_dir, "test.pdf")
    result = os.system(f"word-search some test words -o {temp_path}")
    assert get_exit_status(result) == 0 and temp_path.exists()


def test_export_csv(temp_dir):
    temp_path = pathlib.Path.joinpath(temp_dir, "test.csv")
    result = os.system(f"word-search some test words -o {temp_path}")
    assert get_exit_status(result) == 0 and temp_path.exists()


def test_random_word_valid_input():
    result = os.system("word-search -r 20")
    assert get_exit_status(result) == 0


def test_random_word_invalid_input():
    result = os.system("word-search -r 100")
    assert get_exit_status(result) == 2


def test_size_valid_input():
    result = os.system("word-search some test words -s 20")
    assert get_exit_status(result) == 0


def test_size_invalid_input():
    result = os.system("word-search some test words -s 100")
    assert get_exit_status(result) == 2


def test_dunder_main_entry_point():
    result = os.system("python -m word_search_generator.__main__ some test words")
    assert get_exit_status(result) == 0


def test_cli_import_entry_point():
    result = os.system("python -m word_search_generator.cli some test words")
    assert get_exit_status(result) == 0
