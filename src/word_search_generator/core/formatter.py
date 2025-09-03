from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from . import GameType


class ExportFormat(Enum):
    """Supported export formats for puzzle output.

    This enum defines all valid export formats that can be used when saving
    word search puzzles to files. Each format has specific characteristics:

    - CSV: Comma-separated values, suitable for spreadsheet applications
    - JSON: JavaScript Object Notation, structured data format
    - PDF: Portable Document Format, ready-to-print puzzle format
    """

    CSV = "CSV"
    JSON = "JSON"
    PDF = "PDF"

    def __str__(self) -> str:
        """Return the string value of the format.

        Returns:
            The format name as a string (e.g., "PDF", "CSV", "JSON").
        """
        return self.value

    @classmethod
    def from_string(cls, format_str: str) -> ExportFormat:
        """Create an ExportFormat from a string, case-insensitive.

        Args:
            format_str: Format string (case-insensitive).

        Returns:
            The corresponding ExportFormat enum value.

        Raises:
            ValueError: If the format string is not supported.
        """
        format_upper = format_str.upper()
        for fmt in cls:
            if fmt.value.upper() == format_upper:
                return fmt
        raise ValueError(f"Unsupported export format: {format_str}")


class Formatter(ABC):
    """Base class for game output formatting.

    To implement a custom formatter, subclass this class and implement
    the required abstract methods for displaying and saving games.
    """

    @abstractmethod
    def show(self, game: GameType) -> str:
        """Return a string representation of the game.

        Args:
            game: The game instance to display.

        Returns:
            String representation of the game.
        """

    @abstractmethod
    def save(
        self, game: GameType, path: str | Path, format: ExportFormat = ExportFormat.PDF
    ) -> Path:
        """Save the current puzzle to a file.

        Args:
            game: The game instance to save.
            path: File save path.
            format: Output format. Defaults to ExportFormat.PDF.

        Returns:
            Final save path of the created file.
        """
