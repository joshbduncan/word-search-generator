import random
from collections import defaultdict, Counter
from enum import Enum
from math import sqrt, ceil
from typing import NamedTuple

from attr import dataclass
from fontTools.misc.bezierTools import Intersection

from word_search_generator import WordSearch
from word_search_generator.core import Generator, GameType
from word_search_generator.core.directions import Direction, DirectionSet
from word_search_generator.core.game import Puzzle, MissingWordError, WordSet
from word_search_generator.core.generator import retry, WordFitError
from word_search_generator.core.word import Position, Word


class CellType(Enum):
    OUTSIDE = " "
    INSIDE = "X"
    HEAD = "*"
    LETTER = "+"


def make_cw_puzzle(placed_words: WordSet, dimensions: Position) -> Puzzle:
    p: list[list[CellType]] = [
        [CellType.INSIDE for _ in range(dimensions.column)]
        for _ in range(dimensions.row)
    ]  # cw.size so coords match before cropping (move to Generator)

    for w in placed_words:
        for row, col in w.coordinates:
            if p[row][col] is CellType.HEAD:
                continue
            p[row][col] = CellType.LETTER
        p[w.start_row][w.start_column] = CellType.HEAD

    def get_neighbors(r: int, c: int) -> set[CellType]:
        def check_pos(dr: int, dc: int) -> CellType:
            try:
                return p[r + dr][c + dc]
            except IndexError:
                return CellType.OUTSIDE

        return {
            check_pos(-1, 0),  # above
            check_pos(1, 0),  # below
            check_pos(0, -1),  # left
            check_pos(0, 1),  # right
        }

    def is_boundary(r: int, c: int) -> bool:
        return CellType.OUTSIDE in get_neighbors(r, c)

    for row in range(dimensions.row):
        for col in range(dimensions.column):
            if is_boundary(row, col):
                p[row][col] = CellType.OUTSIDE

    return [[str(c) for c in row] for row in p]


class CrosswordFromWordSearch(Generator):
    def generate(self, game: GameType) -> Puzzle:
        # Try generating increasingly-large WordSearch until all words fit
        size = ceil(sqrt(len("".join(str(w) for w in game.words))) + 1)

        @retry(3)
        def make_ws(s: int):
            return WordSearch(
                level=1, size=s, preprocessed_words=game.words, require_all_words=True
            )

        while True:
            try:
                self.ws = make_ws(size)
                break
            except MissingWordError:
                size += 1

        return make_cw_puzzle(
            self.ws.placed_words, Position(self.ws.size, self.ws.size)
        )


@dataclass
class _Cell:
    letter: str = ""
    available_directions: DirectionSet = {Direction.ACROSS, Direction.DOWN}

    def place_letter(self, l: str, direction: Direction) -> None:
        self.letter = l
        self.available_directions -= {direction}


class CrosswordGenerator(Generator):
    MAX_TRIES_PER_WORD: int = 3

    def generate(self, game: GameType) -> Puzzle:
        # go nuts with a Dict and forcing intersections
        self.puzzle: dict[Position, _Cell] = defaultdict(_Cell)
        self.word_list = sorted(game.words)
        first_word = self.word_list[0]
        retry_queue: Counter[Word] = Counter(self.word_list[1:])
        self.failed_words: list[Word] = []

        # place first word
        self.place_word(
            first_word,
            Position(0, 0),
            random.choice([Direction.ACROSS, Direction.DOWN]),
        )

        # place the rest of the words
        while retry_queue:
            for word, attempts in retry_queue.items():
                if attempts > self.MAX_TRIES_PER_WORD:
                    retry_queue.pop(word)
                    self.failed_words.append(word)
                    continue  # we're done here
                possibilities = self.find_candidate_intersections(word)
                if not possibilities:
                    retry_queue[word] += 1
                    continue  # no possible fits, try after something else is placed
                # choose a possibility
                # currently works randomly; perhaps alter this to encourage density
                self.place_word(word, random.choice(possibilities))
                retry_queue.pop(word)

        # raise error if unplaced words
        # this may be unnecessary thanks to Game.require_all_words,
        # test removing it later
        if any(w.mandatory for w in self.failed_words):
            raise MissingWordError(
                f"Failed to place the following words {self.failed_words}"
            )

        game.number_words()
        return make_cw_puzzle(game.placed_words, self.recenter())

    @property
    def open_letter_list(self) -> dict[str, list[tuple[Position, Direction]]]:
        l = defaultdict(list)
        for pos, cell in self.puzzle.items():
            for d in cell.available_directions:
                l[cell.letter].append((pos, d))
        return l

    class Intersection(NamedTuple):
        pos_intersect: Position
        direction: Direction
        offset: int

        @property
        def pos_head(self) -> Position:
            return self.pos_intersect - self.direction * self.offset

    def find_candidate_intersections(self, w: Word) -> list[Intersection]:
        return [
            Intersection(pos, direct, idx)
            for idx, letter in enumerate(w.text)
            for pos, direct in self.open_letter_list[letter]
        ]

    def find_possible_fits(self, w: Word) -> list[Intersection]:
        return [
            fit
            for fit in self.find_candidate_intersections(w)
            if self.place_word(w, fit.pos_head, fit.direction, test=True)
        ]

    def matches(self, p: Position, l: str) -> bool:
        if not self.puzzle[p]:
            return True
        if self.puzzle[p].letter == l:
            return True
        return False

    def place_word(
        self,
        w: Word,
        position: Position | Intersection,
        direction: Direction = None,
        *,
        test: bool = False,
    ) -> bool:
        if isinstance(position, self.Intersection):
            direction = position.direction
            position = position.pos_head
        if not Direction:
            raise ValueError("No direction specified")
        # test the fit
        for pos, letter in enumerate(w.text):
            p: Position = position + direction * pos
            if not self.matches(p, letter):
                if test:
                    return False
                raise WordFitError(f"Conflict when placing {letter} at {p}.")
        if test:
            return True
        # commit the change to the Puzzle
        for pos, letter in enumerate(w.text):
            self.puzzle[position + direction * pos].place_letter(letter, direction)
        w.position = position
        w.direction = direction
        return True

    def recenter(self) -> Position:
        min_row, min_col = 999, 999
        for p in self.puzzle.keys():
            min_row = min(min_row, p.row)
            min_col = min(min_col, p.column)
        offset = Position(min_row, min_col)

        self.puzzle = {pos - offset: char for pos, char in self.puzzle.keys()}
        for word in self.word_list:
            word.position -= offset
        max_row, max_col = 0, 0
        for p in self.puzzle.keys():
            max_row = max(max_row, p.row)
            max_col = max(max_col, p.column)
        return Position(max_row + 1, max_col + 1)  # for `_ in range()`
