import os
import pathlib


def test_entrypoint():
    exit_status = os.system("word-search --help")
    assert exit_status == 0


def test_no_words_provided():
    exit_status = os.system("word-search")
    assert os.WEXITSTATUS(exit_status) == 1


def test_just_words():
    exit_status = os.system("word-search some test words")
    assert exit_status == 0


def test_stdin():
    exit_status = os.system("echo computer robot soda | word-search")
    assert os.WEXITSTATUS(exit_status) == 0


def test_export_pdf(temp_dir):
    temp_path = temp_dir + "/test.pdf"
    exit_status = os.system(f"word-search some test words -e pdf -o {temp_path}")
    assert exit_status == 0 and pathlib.Path(temp_path).exists()


def test_export_csv(temp_dir):
    temp_path = temp_dir + "/test.csv"
    exit_status = os.system(f"word-search some test words -e csv -o {temp_path}")
    assert exit_status == 0 and pathlib.Path(temp_path).exists()


def test_invalid_export_location():
    exit_status = os.system("word-search some test words -e csv -o ~/RANDOMTESTLOC")
    assert os.WEXITSTATUS(exit_status) == 1


def test_random_word_valid_input():
    exit_status = os.system("word-search -r 20")
    assert os.WEXITSTATUS(exit_status) == 0


def test_random_word_invalid_input():
    exit_status = os.system("word-search -r 100")
    assert os.WEXITSTATUS(exit_status) == 2


def test_size_valid_input():
    exit_status = os.system("word-search some test words -s 20")
    assert os.WEXITSTATUS(exit_status) == 0


def test_size_invalid_input():
    exit_status = os.system("word-search some test words -s 100")
    assert os.WEXITSTATUS(exit_status) == 2


def test_dunder_main_entry_point():
    exit_status = os.system("python -m word_search_generator.__main__ some test words")
    assert os.WEXITSTATUS(exit_status) == 0


def test_cli_import_entry_point():
    exit_status = os.system("python -m word_search_generator.cli some test words")
    assert os.WEXITSTATUS(exit_status) == 0
