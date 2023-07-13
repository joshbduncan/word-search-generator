from word_search_generator.game.word_search import WordSearch
from word_search_generator.validator import (
    NoPalindromes,
    NoPunctuation,
    NoSingleLetterWords,
    NoSubwords,
)


def test_no_palindromes_valid():
    validator = NoPalindromes()
    assert validator.validate("turtle")


def test_no_palindromes_invalid():
    validator = NoPalindromes()
    assert not validator.validate("level")


def test_no_palindromes_puzzle():
    ws = WordSearch(
        "level is a palindrome, so is mom and peep", validators=[NoPalindromes()]
    )
    words = (word.text for word in ws.placed_words)
    assert "level" not in words
    assert "mom" not in words
    assert "peep" not in words


def test_no_punctuation_valid():
    validator = NoPunctuation()
    assert validator.validate("elephant")


def test_no_punctuation_invalid():
    validator = NoPunctuation()
    assert not validator.validate("it's")


def test_no_single_letter_words_valid():
    validator = NoSingleLetterWords()
    assert validator.validate("newt")


def test_no_single_letter_words_invalid():
    validator = NoSingleLetterWords()
    assert not validator.validate("n")


def test_no_single_letter_words_in_puzzle():
    ws = WordSearch("i is a single letter word", validators=[NoSingleLetterWords()])
    words = (word.text for word in ws.placed_words)
    assert "i" not in words
    assert "1" not in words


def test_no_subwords_valid():
    validator = NoSubwords()
    assert validator.validate("laptop", placed_words=["briefcase", "luggage", "duffle"])


def test_no_subwords_invalid():
    validator = NoSubwords()
    assert not validator.validate("cream", placed_words=["icecream", "cone", "scoop"])
