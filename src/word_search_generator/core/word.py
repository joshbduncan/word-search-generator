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
        """Initialize a Word Search puzzle Word."""
        self.text = text.upper().strip()
        self.start_row: int | None = None
        self.start_column: int | None = None
        self.coordinates: list[tuple[int, int]] = []
        self.direction: Direction | None = None
        self.secret = secret
        self.color = colorsys.hsv_to_rgb(
            random.random(),
            random.randint(42, 98) / 100,
            random.randint(40, 90) / 100,
        )

    def validate(
        self, validators: Iterable[Validator], placed_words: list[str]
    ) -> bool:
        """Validate the word against a list of validators.

        Args:
            validators: Validators to test.
            placed_words: Currently placed puzzle words.

        Raises:
            TypeError: Incorrect validator type provided.

        Returns:
            Word passes all validators.
        """
        for validator in validators:
            if not isinstance(validator, Validator):
                raise TypeError(f"Invalid validator: {validator}.")
            if not validator.validate(self.text, placed_words=placed_words):
                return False
        return True

    @property
    def lowercase(self) -> str:
        """Return lowercase version of the word."""
        if not self.placed:
            return ""
        return self.text.lower()

    @property
    def placed(self) -> bool:
        """Is the word currently placed in a puzzle.

        Note: Used `is not None` since 0 vals for start_row/column are not truthy
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
        """Current start position of the word in the puzzle
        as (start_row, start_column)."""
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
        """Returns a the word position with 1-based indexing
        and a familiar (x, y) coordinate system"""
        return Position(
            self.start_row + 1 if self.start_row is not None else self.start_row,
            (
                self.start_column + 1
                if self.start_column is not None
                else self.start_column
            ),
        )

    @property
    def rich_style(self) -> Style:
        """Returns a rich Style for outputting the word in the cli."""
        r, g, b = (int(v * 255) for v in self.color)
        return Style(bgcolor=f"rgb({r},{g},{b})", bold=True)

    @property
    def key_info(self) -> KeyInfo:
        """Returns the Word placement information formatted
        correctly for a WordSearch puzzle key."""
        return {
            "start": self.position,
            "direction": self.direction,
            "secret": self.secret,
        }

    @property
    def key_info_json(self) -> KeyInfoJson:
        """Returns the Word placement information formatted
        correctly for a WordSearch puzzle key used in the JSON property."""
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
        """Return a string representation of the Word placement
        information formatted correctly for a WordSearch puzzle key
        when the WordSearch object it output using the `print()` or
        `.show()` method.

        Args:
            bbox: The current puzzle bounding box.
            lowercase: Should words be lowercase. Defaults to False.
            reversed_letters: Should words letters be reversed. Defaults to False.

        Returns:
            Word placement information.
        """
        if not self.placed:
            return ""
        col, row = self.offset_position_xy(bbox)
        word_text = self.lowercase if lowercase else self.text
        if reversed_letters:
            word_text = word_text[::-1]
        return (
            f"{'*' if self.secret else ''}"
            + f"{word_text} "
            + f"{self.direction.name if self.direction else self.direction}"
            + f" @ {(col, row)}"
        )

    def offset_position_xy(self, bbox: BoundingBox) -> Position:
        """Returns a string representation of the word position with
        1-based indexing and a familiar (x, y) coordinate system. The
        position will be offset by the puzzle bounding box when a puzzle
        has been masked.

        Args:
            bbox (BoundingBox): The current
                puzzle bounding box.
        """
        return Position(
            (
                self.start_column + 1 - bbox[0][0]
                if self.start_column is not None
                else self.start_column
            ),
            (
                self.start_row + 1 - bbox[0][1]
                if self.start_row is not None
                else self.start_row
            ),
        )

    def offset_coordinates(self, bbox: BoundingBox) -> list[Position]:
        """Returns a list of the Word letter coordinates, offset
        by the puzzle bounding box.

        Args:
            bbox (BoundingBox): The current
                puzzle bounding box.
        """
        return [
            Position(
                x + 1 - bbox[0][0] if x is not None else x,
                y + 1 - bbox[0][1] if y is not None else y,
            )
            for y, x in self.coordinates
        ]

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
