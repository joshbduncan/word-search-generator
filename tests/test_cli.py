import os
import pathlib


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


def test_just_words():
    result = os.system("word-search some test words")
    assert get_exit_status(result) == 0


def test_with_secret_words():
    result = os.system("word-search -r 10 -x fhqwhgads,dewlap")
    assert get_exit_status(result) == 0


def test_stdin():
    result = os.system("echo computer robot soda | word-search")
    assert get_exit_status(result) == 0


def test_export_pdf(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    result = os.system(f"word-search some test words -o {tmp_path}")
    assert get_exit_status(result) == 0 and tmp_path.exists()


def test_export_csv(tmp_path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    result = os.system(f"word-search some test words -o {tmp_path}")
    assert get_exit_status(result) == 0 and tmp_path.exists()


def test_random_word_valid_input():
    result = os.system("word-search -r 20")
    assert get_exit_status(result) == 0


def test_random_word_invalid_input():
    result = os.system("word-search -r 1000")
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


def test_no_words_provided():
    result = os.system("word-search -l 2")
    assert get_exit_status(result) == 1


def test_level_difficulty_argument():
    result = os.system("word-search -r 5 -l 2")
    assert get_exit_status(result) == 0


def test_custom_difficulty_argument():
    result = os.system("word-search -r 5 -d N,W")
    assert get_exit_status(result) == 0


def test_invalid_difficulty_argument():
    result = os.system("word-search -r 5 -d NNW")
    assert get_exit_status(result) == 1


def test_invalid_argparse_difficulty_argument():
    result = os.system("word-search -r 5 -d 1,N")
    assert get_exit_status(result) == 2


def test_custom_difficulty_level_as_string():
    result = os.system("word-search -r 5 -d 3")
    assert get_exit_status(result) == 0
