import os
import pathlib
import tempfile


TEMP_DIR = tempfile.TemporaryDirectory()


def test_entrypoint():
    exit_status = os.system("word-search --help")
    assert exit_status == 0


def test_no_words_provided():
    exit_status = os.system("word-search")
    assert os.WEXITSTATUS(exit_status) == 1


def test_just_words():
    exit_status = os.system("word-search some test words")
    assert exit_status == 0


def test_export_pdf():
    temp_path = TEMP_DIR.name + "/test.pdf"
    exit_status = os.system(f"word-search some test words -e pdf -o {temp_path}")
    assert exit_status == 0 and pathlib.Path(temp_path).exists()


def test_export_csv():
    temp_path = TEMP_DIR.name + "/test.csv"
    exit_status = os.system(f"word-search some test words -e csv -o {temp_path}")
    assert exit_status == 0 and pathlib.Path(temp_path).exists()


def test_invalid_export_location():
    exit_status = os.system("word-search some test words -e csv -o ~/RANDOMTESTLOC")
    assert os.WEXITSTATUS(exit_status) == 1
