from pathlib import Path

from word_search_generator import WordSearch
from word_search_generator.word_search._formatter import WordSearchFormatter


def test_formatter_show_with_sorting():
    """Test formatter show method with sorting enabled."""
    ws = WordSearch("zebra,apple,cat")
    formatter = WordSearchFormatter()

    output = formatter.show(ws, sort_words=True)

    # Check that words appear in alphabetical order
    assert "APPLE, CAT, ZEBRA" in output


def test_formatter_show_without_sorting():
    """Test formatter show method with sorting disabled."""
    ws = WordSearch("zebra,apple,cat")
    formatter = WordSearchFormatter()

    output = formatter.show(ws, sort_words=False)

    # Check that words appear in original order
    assert "ZEBRA, APPLE, CAT" in output


def test_formatter_save_csv_with_sorting(tmp_path):
    """Test formatter save CSV with sorting enabled."""
    ws = WordSearch("dog,cat,bat")
    formatter = WordSearchFormatter()
    csv_file = tmp_path / "test.csv"

    formatter.save(ws, csv_file, format="CSV", sort_words=True)
    assert csv_file.exists()

    content = csv_file.read_text()
    # Check that words are in sorted order in CSV
    bat_pos = content.find("BAT")
    cat_pos = content.find("CAT")
    dog_pos = content.find("DOG")

    assert bat_pos < cat_pos < dog_pos


def test_formatter_save_csv_without_sorting(tmp_path):
    """Test formatter save CSV with sorting disabled."""
    ws = WordSearch("dog,cat,bat")
    formatter = WordSearchFormatter()
    csv_file = tmp_path / "test.csv"

    formatter.save(ws, csv_file, format="CSV", sort_words=False)
    assert csv_file.exists()

    content = csv_file.read_text()
    # Check that words are in original order in CSV
    dog_pos = content.find("DOG")
    cat_pos = content.find("CAT")
    bat_pos = content.find("BAT")

    assert dog_pos < cat_pos < bat_pos


def test_formatter_save_json_with_sorting(tmp_path):
    """Test formatter save JSON with sorting enabled."""
    ws = WordSearch("zebra,apple")
    formatter = WordSearchFormatter()
    json_file = tmp_path / "test.json"

    formatter.save(ws, json_file, format="JSON", sort_words=True)
    assert json_file.exists()

    import json

    with open(json_file) as f:
        data = json.load(f)

    words = data.get("words", [])
    assert len(words) == 2
    # Should contain both words
    assert "APPLE" in words
    assert "ZEBRA" in words


def test_formatter_save_json_without_sorting(tmp_path):
    """Test formatter save JSON with sorting disabled."""
    ws = WordSearch("zebra,apple")
    formatter = WordSearchFormatter()
    json_file = tmp_path / "test.json"

    formatter.save(ws, json_file, format="JSON", sort_words=False)
    assert json_file.exists()

    import json

    with open(json_file) as f:
        data = json.load(f)

    words = data.get("words", [])
    assert len(words) == 2
    # Should contain both words
    assert "APPLE" in words
    assert "ZEBRA" in words


def test_formatter_save_pdf_with_sorting(tmp_path):
    """Test formatter save PDF with sorting enabled."""
    ws = WordSearch("cat,bat,hat")
    formatter = WordSearchFormatter()
    pdf_file = tmp_path / "test.pdf"

    saved_path = formatter.save(ws, pdf_file, format="PDF", sort_words=True)
    assert Path(saved_path).exists()


def test_formatter_save_pdf_without_sorting(tmp_path):
    """Test formatter save PDF with sorting disabled."""
    ws = WordSearch("cat,bat,hat")
    formatter = WordSearchFormatter()
    pdf_file = tmp_path / "test.pdf"

    saved_path = formatter.save(ws, pdf_file, format="PDF", sort_words=False)
    assert Path(saved_path).exists()


def test_formatter_answer_key_sorting():
    """Test that answer key respects sorting parameter."""
    ws = WordSearch("zebra,apple,cat")
    formatter = WordSearchFormatter()

    # Test with sorting
    output_sorted = formatter.show(ws, sort_words=True)
    # Test without sorting
    output_unsorted = formatter.show(ws, sort_words=False)

    # Both outputs should contain all words but in different order
    for word in ["APPLE", "CAT", "ZEBRA"]:
        assert word in output_sorted
        assert word in output_unsorted

    # The order should be different
    assert output_sorted != output_unsorted
