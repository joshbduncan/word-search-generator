import colorsys
import random
from collections.abc import Iterable
from typing import NamedTuple, TypedDict

from rich.style import Style

from ..utils import BoundingBox
from .game import Direction
from .validator import Validator


class Position(NamedTuple):
    row: int | None
    column: int | None


class KeyInfo(TypedDict):
    start: Position | None
    direction: Direction | None
    secret: bool


class KeyInfoJson(TypedDict):
    start_row: int | None
    start_col: int | None
    direction: str | None
    secret: bool


class Word:
    """This class represents a Word within a WordSearch puzzle."""

    def __init__(
        self,
        text: str,
        secret: bool = False,
    ) -> None:
        """Initialize a Word Search puzzle Word.

        Args:
            text: The word text to use in the puzzle.
            secret: Whether this is a secret word (hidden from key).

        Raises:
            ValueError: If text is empty or contains only whitespace.
        """
        if not isinstance(text, str):
            raise TypeError(f"Word text must be a string, got {type(text).__name__}")

        cleaned_text = text.upper().strip()
        if not cleaned_text:
            raise ValueError("Word text cannot be empty or contain only whitespace")

        self.text = cleaned_text
        self.start_row: int | None = None
        self.start_column: int | None = None
        self.coordinates: list[tuple[int, int]] = []
        self.direction: Direction | None = None
        self.secret = secret
        self.color: tuple[float, float, float] = colorsys.hsv_to_rgb(
            h=random.random(),
            s=random.randint(42, 98) / 100,
            v=random.randint(40, 90) / 100,
        )

    def validate(
        self, validators: Iterable[Validator], placed_words: list[str]
    ) -> bool:
        """Validate the word against a list of validators.

        Args:
            validators: Validators to test against the word.
            placed_words: Currently placed puzzle words.

        Raises:
            TypeError: If validator is not a Validator instance.
            ValueError: If validators or placed_words is None.

        Returns:
            True if the word passes all validators, False otherwise.
        """
        if validators is None:
            raise ValueError("Validators cannot be None")
        if placed_words is None:
            raise ValueError("Placed words cannot be None")

        for validator in validators:
            if not isinstance(validator, Validator):
                raise TypeError(
                    f"Expected Validator instance, got {type(validator).__name__}: "
                    f"{validator}"
                )

            if not validator.validate(self.text, placed_words=placed_words):
                return False
        return True

    @property
    def lowercase(self) -> str:
        """Return lowercase version of the word.

        Returns:
            Lowercase word text if placed, empty string if not placed.
        """
        if not self.placed:
            return ""
        return self.text.lower()

    @property
    def placed(self) -> bool:
        """Check if the word is currently placed in a puzzle.

        Returns:
            True if the word has a start position and direction, False otherwise.

        Note:
            Uses `is not None` since 0 values for start_row/column are not truthy.
        """
        return all(
            (
                self.start_column is not None,
                self.start_row is not None,
                self.direction is not None,
            )
        )

    @property
    def position(self) -> Position:
        """Get the current start position of the word in the puzzle.

        Returns:
            Position namedtuple containing (start_row, start_column).
        """
        return Position(self.start_row, self.start_column)

    @position.setter
    def position(self, value: Position) -> None:
        """Set the start position of the Word in the puzzle.

        Args:
            value: Tuple of (row, column)
        """
        self.start_row = value.row
        self.start_column = value.column

    @property
    def position_xy(self) -> Position:
        """Get the word position with 1-based indexing and (x, y) coordinate system.

        Returns:
            Position namedtuple with 1-based coordinates (row + 1, column + 1).
        """
        return Position(
            self._add_one_if_not_none(self.start_row),
            self._add_one_if_not_none(self.start_column),
        )

    def _add_one_if_not_none(self, value: int | None) -> int | None:
        """Helper method to add 1 to a value if it's not None.

        Args:
            value: Integer value or None.

        Returns:
            value + 1 if value is not None, otherwise None.
        """
        return value + 1 if value is not None else None

    @property
    def rich_style(self) -> Style:
        """Get a Rich Style object for colored CLI output.

        Returns:
            Rich Style with random background color and bold text.
        """
        r, g, b = (int(v * 255) for v in self.color)
        return Style(bgcolor=f"rgb({r},{g},{b})", bold=True)

    @property
    def key_info(self) -> KeyInfo:
        """Get word placement information for puzzle key display.

        Returns:
            KeyInfo TypedDict containing start position, direction, and secret status.
        """
        return {
            "start": self.position,
            "direction": self.direction,
            "secret": self.secret,
        }

    @property
    def key_info_json(self) -> KeyInfoJson:
        """Get word placement information formatted for JSON serialization.

        Returns:
            KeyInfoJson TypedDict with separate row/column fields and string direction.
        """
        return {
            "start_row": self.start_row,
            "start_col": self.start_column,
            "direction": self.direction.name if self.direction else None,
            "secret": self.secret,
        }

    def key_string(
        self,
        bbox: BoundingBox,
        lowercase: bool = False,
        reversed_letters: bool = False,
    ) -> str:
        """Get formatted string representation for puzzle key display.

        Used when outputting WordSearch objects via print() or show() methods.

        Args:
            bbox: The current puzzle bounding box.
            lowercase: Whether to display word in lowercase.
            reversed_letters: Whether to reverse the word letters.

        Returns:
            Formatted word placement information string, or empty if not placed.
        """
        if not self.placed:
            return ""

        if self.direction is None:
            raise ValueError("Word direction cannot be None when placed")

        col, row = self.offset_position_xy(bbox)
        word_text = self.lowercase if lowercase else self.text

        if reversed_letters:
            word_text = word_text[::-1]

        secret_marker = "*" if self.secret else ""
        direction_name = self.direction.name

        return f"{secret_marker}{word_text} {direction_name} @ {(col, row)}"

    def offset_position_xy(self, bbox: BoundingBox) -> Position:
        """Get word position with 1-based indexing, offset by bounding box.

        The position is adjusted for masked puzzles by subtracting the bounding
        box offset and adding 1 for 1-based indexing.

        Args:
            bbox: The current puzzle bounding box.

        Returns:
            Position with (column, row) offset by bounding box.
        """
        return Position(
            self._offset_coordinate(self.start_column, bbox[0][0]),
            self._offset_coordinate(self.start_row, bbox[0][1]),
        )

    def offset_coordinates(self, bbox: BoundingBox) -> list[Position]:
        """Get list of word letter coordinates, offset by bounding box.

        Args:
            bbox: The current puzzle bounding box.

        Returns:
            List of Position objects for each letter coordinate.
        """
        return [
            Position(
                self._offset_coordinate(x, bbox[0][0]),
                self._offset_coordinate(y, bbox[0][1]),
            )
            for y, x in self.coordinates
        ]

    def _offset_coordinate(self, value: int | None, offset: int) -> int | None:
        """Helper method to apply bounding box offset with 1-based indexing.

        Args:
            value: Original coordinate value or None.
            offset: Bounding box offset to subtract.

        Returns:
            value + 1 - offset if value is not None, otherwise None.
        """
        return value + 1 - offset if value is not None else None

    def remove_from_puzzle(self):
        """Remove word placement details when a puzzle is reset."""
        self.start_row = None
        self.start_column = None
        self.coordinates = []
        self.direction = None

    def __bool__(self) -> bool:
        """Returns the truthiness of a word.
        Should always return true, except for the null word."""
        return bool(self.text)

    def __eq__(self, __o: object) -> bool:
        """Returns True if both instances have the same text."""
        if not isinstance(__o, Word):
            return False
        return self.text == __o.text

    def __hash__(self) -> int:
        """Returns the hashes value of the word text."""
        return hash(self.text)

    def __len__(self) -> int:
        """Returns the length of the word text."""
        return len(self.text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.text}', " + f"{self.secret})"

    def __str__(self) -> str:
        return self.text


# in the future, add allowed_directions = set() and priority = 999
NULL_WORD = Word("", True)
