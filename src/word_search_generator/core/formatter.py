from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from .game import Game


class Formatter(ABC):
    """Base class for Game output.

    To implement your own `Formatter`, subclass this class.
    """

    @abstractmethod
    def show(self, game: Game, *args, **kwargs) -> str:
        """Return a string representation of the game."""

    @abstractmethod
    def save(
        self,
        game: Game,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        """Save the current puzzle to a file.

        Args:
            game (Game): Parent `WordSearch` puzzle.
            path (str | Path): File save path.
            format (str, optional): Type of file to save ("CSV", "JSON", "PDF").
                Defaults to "PDF".
            solution (bool, optional): Include solution with the saved file.
                For CSV and JSON files, only placed word characters will be included.
                For PDF, a separate solution page will be included with word
                characters highlighted in red. Defaults to False.

        Returns:
            str: Final save path of the file.
        """
