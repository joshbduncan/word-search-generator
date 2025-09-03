"""Word validation system for word search generation.

This module provides an extensible validation framework for filtering words
based on various criteria. Validators are used to ensure words meet specific
requirements before being placed in word search puzzles.

The system includes built-in validators for common requirements like minimum
length, punctuation filtering, palindrome detection, and subword checking.
Custom validators can be created by subclassing the Validator base class.
"""

import string
from abc import ABC, abstractmethod


class Validator(ABC):
    """Base class for the validation of words.

    To implement your own `Validator`, subclass this class.

    Example:
        ```python
        class Palindrome(Validator):
            def validate(self, value: str) -> bool:
                return value == value[::-1]
        ```
    """

    @abstractmethod
    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate the value.

        Args:
            value: The word to validate.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments. Some validators may expect
                specific kwargs (e.g., 'placed_words' for NoSubwords).

        Returns:
            True if the value passes validation, False otherwise.
        """


class NoSingleLetterWords(Validator):
    """A validator to ensure words have more than one character.

    Example:
        >>> validator = NoSingleLetterWords()
        >>> validator.validate("a")  # False
        >>> validator.validate("cat")  # True
    """

    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate that the word has more than one character.

        Args:
            value: The word to validate.

        Returns:
            True if the word has more than one character, False otherwise.
        """
        if not value:
            return False
        return len(value) > 1


class NoPunctuation(Validator):
    """A validator to ensure words don't contain punctuation characters.

    Example:
        >>> validator = NoPunctuation()
        >>> validator.validate("don't")  # False
        >>> validator.validate("hello")  # True
    """

    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate that the word contains no punctuation.

        Args:
            value: The word to validate.

        Returns:
            True if the word has no punctuation, False otherwise.
        """
        if not value:
            return False
        return not any(c in string.punctuation for c in value)


class NoPalindromes(Validator):
    """A validator to ensure words are not palindromes.

    Example:
        >>> validator = NoPalindromes()
        >>> validator.validate("racecar")  # False
        >>> validator.validate("hello")  # True
    """

    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate that the word is not a palindrome.

        Args:
            value: The word to validate.

        Returns:
            True if the word is not a palindrome, False otherwise.
        """
        if not value:
            return False

        # Optimize by comparing characters from both ends
        value_lower = value.lower()
        left, right = 0, len(value_lower) - 1

        while left < right:
            if value_lower[left] != value_lower[right]:
                return True
            left += 1
            right -= 1

        return False  # It's a palindrome


class NoSubwords(Validator):
    """A validator to ensure words are not subwords of existing words.

    Checks that the word is not contained within any previously placed words,
    and vice versa. Also checks reversed versions to catch overlaps in both
    directions of word search grids.

    Example:
        >>> validator = NoSubwords()
        >>> validator.validate("cat", placed_words=["cats"])  # False
        >>> validator.validate("dog", placed_words=["cats"])  # True
    """

    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate that the word is not a subword of existing words.

        Args:
            value: The word to validate.
            **kwargs: Must contain 'placed_words' key with list of existing words.

        Returns:
            True if the word is not a subword, False otherwise.
        """
        if not value:
            return False

        placed_words = kwargs.get("placed_words", [])
        if not placed_words:
            return True

        value_lower = value.lower()
        value_reversed_lower = value_lower[::-1]

        for existing_word in placed_words:
            if not existing_word:
                continue

            existing_lower = existing_word.lower()
            existing_reversed_lower = existing_lower[::-1]

            # Check all four combinations of substring relationships
            if (
                self._is_subword(value_lower, existing_lower)
                or self._is_subword(value_reversed_lower, existing_lower)
                or self._is_subword(existing_lower, value_lower)
                or self._is_subword(existing_reversed_lower, value_lower)
            ):
                return False

        return True

    def _is_subword(self, word1: str, word2: str) -> bool:
        """Check if word1 is a substring of word2.

        Args:
            word1: The potential substring.
            word2: The string to search within.

        Returns:
            True if word1 is found within word2, False otherwise.
        """
        return word1 in word2
