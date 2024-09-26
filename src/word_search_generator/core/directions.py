from enum import Enum
from typing import Callable, Iterable, TypeAlias


class Direction(Enum):
    """
    If you want custom directions, like `"skipE": (0, 2)`, this is the
    place to monkey-patch them in.

    Tuples are listed in (∂row, ∂col) pairs, presumably b/c that makes
    it easier to use with the Puzzle = list[list[chr]] format
    """

    N = (-1, 0)
    NE = (-1, 1)
    E = (0, 1)
    SE = (1, 1)
    S = (1, 0)
    SW = (1, -1)
    W = (0, -1)
    NW = (-1, -1)

    # Crossword directions
    ACROSS = (0, 1)
    DOWN = (1, 0)

    @property
    def r_move(self) -> int:
        return self.value[0]

    @property
    def c_move(self) -> int:
        return self.value[1]

    @property
    def is_cardinal(self) -> bool:
        """Cardinal directions have 0 movement in one direction"""
        return not self.r_move or not self.c_move

    @property
    def is_diagonal(self) -> bool:
        return not self.is_cardinal

    @property
    def opposite(self) -> "Direction":
        return Direction((-self.r_move, -self.c_move))


DirectionSet: TypeAlias = set[Direction] | frozenset[Direction]
_ALL_DIRECTIONS = frozenset(
    {
        Direction.N,
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    }
)


def invert_ds(ds: DirectionSet, freeze: bool = False) -> DirectionSet:
    """Essentially DirectionSet.__not__()"""
    s: Callable[..., DirectionSet] = frozenset if freeze else set
    return s(_ALL_DIRECTIONS - ds)


def reverse_directions(
    ds: Iterable[Direction], output_type: Callable[..., Iterable[Direction]] = set
) -> Iterable[Direction]:
    """Makes all the directions in the Iterable point the other way."""
    return output_type(d.opposite for d in ds)


class NamedDirectionSet:
    CROSSWORD = frozenset({Direction.ACROSS, Direction.DOWN})
    ALL = _ALL_DIRECTIONS
    ANY = reverse_directions(_ALL_DIRECTIONS, frozenset)
    NONE = invert_ds(_ALL_DIRECTIONS, True)
    ZERO = reverse_directions(NONE, frozenset)
    FORWARD = frozenset(
        {  # right-facing or down
            Direction.NE,
            Direction.E,
            Direction.SE,
            Direction.S,
        }
    )
    BACKWARD = reverse_directions(FORWARD, frozenset)
    DIAGONAL = frozenset(d for d in _ALL_DIRECTIONS if d.is_diagonal)
    CARDINAL = frozenset(d for d in _ALL_DIRECTIONS if d.is_cardinal)


NDS = NamedDirectionSet
# puzzle difficulty levels
LEVEL_DIRS: dict[int, DirectionSet] = {
    -1: NDS.NONE,  # no valid directions
    1: NDS.CROSSWORD,  # right or down
    2: NDS.FORWARD,
    3: _ALL_DIRECTIONS,
    4: {  # no E or S for better hiding
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    5: {  # no E
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    7: NDS.DIAGONAL,
    8: NDS.CARDINAL,
}
