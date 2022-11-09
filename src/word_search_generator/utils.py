from __future__ import annotations

import copy
import random
import string
import sys
from math import log2
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Sized, Tuple

from . import config
from .word import Direction, Word

if TYPE_CHECKING:  # pragma: no cover
    from . import DirectionSet, Key, WordSearch
    from .puzzle import PuzzleGrid
    from .word import Wordlist


def calc_puzzle_size(words: Wordlist, level: Sized, size: Optional[int] = None) -> int:
    """Calculate the puzzle grid size."""
    all_words = list(word.text for word in words)
    longest_word_length = len(max(all_words, key=len))
    shortest_word_length = len(min(all_words, key=len))
    if not size:
        longest = max(10, longest_word_length)
        # calculate multiplier for larger word lists so that most have room to fit
        multiplier = len(all_words) / 15 if len(all_words) > 15 else 1
        # level lengths in config.py are nice multiples of 2
        l_size = log2(len(level)) if level else 1  # protect against log(0) in tests
        size = round(longest + l_size * 2 * multiplier)
    else:
        if size < shortest_word_length:
            print(
                "Puzzle sized adjust to fit word with the shortest length.",
                file=sys.stderr,
            )
            size = shortest_word_length + 1
    return size


def build_puzzle(size: int, char: str) -> PuzzleGrid:
    return [[char] * size for _ in range(size)]


def out_of_bounds(size: int, position: Tuple[int, int]) -> bool:
    """Validate `position` is within the current puzzle bounds."""
    width = height = size
    row, col = position
    if row < 0 or col < 0 or row > height - 1 or col > width - 1:
        return True
    return False


def find_bounding_box(grid: List[List[str]]) -> Tuple[int, int, int, int]:
    """Find the ACTIVE area bounding box of the supplied grid."""
    size = len(grid)
    # find the top and bottom edges
    top_edge = 0
    for i in range(size):
        if grid[i].count(config.ACTIVE):
            top_edge = i
            break
    rows_reversed = grid[::-1]
    bottom_edge = 0
    for i in range(size):
        if rows_reversed[i].count(config.ACTIVE):
            bottom_edge = size - i
            break
    # find the left and right edges
    cols = list(zip(*grid))
    left_edge = 0
    for i in range(size):
        if cols[i].count(config.ACTIVE):
            left_edge = i
            break
    right_edge = 0
    cols_reversed = cols[::-1]
    for i in range(size):
        if cols_reversed[i].count(config.ACTIVE):
            right_edge = size - i
            break
    return (top_edge, left_edge, right_edge, bottom_edge)


def cleanup_input(words: str, secret: bool = False) -> Wordlist:
    """Cleanup provided input string. Removing spaces
    one-letter words, and words with punctuation."""
    if not isinstance(words, str):
        raise TypeError(
            "Words must be a string separated by spaces, commas, or new lines"
        )
    # remove new lines
    words = words.replace("\n", ",")
    # remove excess spaces and commas
    word_list = ",".join(words.split(" ")).split(",")
    # iterate through all words and pick first set that match criteria
    word_set: Wordlist = set()
    while word_list and len(word_set) <= config.max_puzzle_words:
        word = word_list.pop(0)
        if (
            len(word) > 1
            and not contains_punctuation(word)
            and not is_palindrome(word)
            and not word_contains_word(word_set, word.upper())
        ):
            word_set.add(Word(word, secret=secret))
    # if no words were left raise exception
    if not word_set:
        raise ValueError("Use words longer than one-character and without punctuation.")
    return word_set


def contains_punctuation(word):
    """Check to see if punctuation is present in the provided string."""
    return any([True if c in string.punctuation else False for c in word])


def is_palindrome(word: str) -> bool:
    """Check is a word in a palindrome."""
    return word == word[::-1]


def word_contains_word(words: Wordlist, word: str) -> bool:
    """Make sure `test_word` cannot be found in any word
    in `words`, going forward or backward."""
    for test_word in words:
        if (
            word in test_word.text.upper()
            or word[::-1] in test_word.text.upper()
            or test_word.text.upper() in word
            or test_word.text.upper()[::-1] in word
        ):
            return True
    return False


def validate_direction_iterable(
    d: Iterable[str | Tuple[int, int] | Direction]
) -> DirectionSet:
    """Validates that all the directions in d are found as keys to
    config.dir_moves and therefore are valid directions."""
    o = set()
    for direction in d:
        if isinstance(direction, Direction):
            o.add(direction)
            continue
        elif isinstance(direction, tuple):
            o.add(Direction(direction))
            continue
        try:
            o.add(Direction[direction.upper().strip()])
        except KeyError:
            raise ValueError(f"'{direction}' is not a valid direction.")
    return o


def validate_level(d) -> DirectionSet:
    """Given a d, try to turn it into a list of valid moves."""
    if isinstance(d, int):  # traditional numeric level
        try:
            return config.level_dirs[d]
        except KeyError:
            raise ValueError(
                f"{d} is not a valid difficulty number"
                + f"[{', '.join([str(i) for i in config.level_dirs.keys()])}]"
            )
    if isinstance(d, str):  # comma-delimited list
        return validate_direction_iterable(d.split(","))
    if isinstance(d, Iterable):  # probably used by external code
        return validate_direction_iterable(d)
    raise TypeError(f"{type(d)} given, not str, int, or Iterable[str]\n{d}")


def direction_set_repr(ds: DirectionSet) -> str:
    return ("'" + ",".join(d.name for d in ds) + "'") if ds else "None"


def highlight_solution(ws: WordSearch) -> PuzzleGrid:
    """Add highlighting to puzzle solution."""
    output: PuzzleGrid = copy.deepcopy(ws.puzzle.puzzle)
    for word in ws.placed_words:
        if (
            word.start_column is not None
            and word.start_row is not None
            and word.direction
        ):  # FIXME: only here for mypy
            x = word.start_column
            y = word.start_row
            for char in word.text:
                output[y][x] = f"\u001b[1m\u001b[31m{char}\u001b[0m"
                x += word.direction.c_move
                y += word.direction.r_move
    return output


def make_header(size: int, text: str) -> str:
    """Generate a header that fits the current puzzle size."""
    hr = "-" * max(11, (size * 2 - 1))
    padding = " " * ((len(hr) - len(text)) // 2)
    return f"""{hr}
{padding}{text}{padding}
{hr}"""


def stringify(puzzle: PuzzleGrid) -> str:
    """Convert puzzle array of nested lists into a string."""
    output = []
    for line in puzzle:
        output.append(" ".join(line))
    return "\n".join(output)


def format_puzzle_for_show(ws: WordSearch, show_solution: bool = False) -> str:
    header = make_header(ws.size, "WORD SEARCH")
    word_list = get_word_list_str(ws.key)
    # highlight solution if provided
    puzzle_list = highlight_solution(ws) if show_solution else ws.puzzle.puzzle
    answer_key_intro = (
        "Answer Key (*= Secret Words)" if ws.placed_secret_words else "Answer Key"
    )
    return f"""{header}
{stringify(puzzle_list)}

Find these words: {word_list if word_list else '<ALL SECRET WORDS>'}
* Words can go {get_level_dirs_str(ws.level)}.

{answer_key_intro}: {get_answer_key_str(ws.placed_words)}"""


def get_level_dirs_str(level: DirectionSet) -> str:
    """Return possible directions for specified level as a string."""
    level_dirs_str = [d.name for d in level]
    level_dirs_str.insert(-1, "and")
    return ", ".join(level_dirs_str)


def get_word_list_str(key: Key) -> str:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return ", ".join(get_word_list_list(key))


def get_word_list_list(key: Key) -> List[str]:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return [k for k in sorted(key.keys()) if not key[k]["secret"]]


def get_answer_key_list(words: Wordlist) -> List[Any]:
    """Return a easy to read answer key for display/export."""
    keys = []
    for w in sorted(words, key=lambda word: word.text):
        keys.append(w.key_string)
    return keys


def get_answer_key_str(words: Wordlist) -> str:
    """Return a easy to read answer key for display."""
    keys = get_answer_key_list(words)
    return ", ".join(keys)


def get_random_words(n: int) -> str:
    return ",".join(random.sample(WORD_LIST, n))


WORD_LIST = [
    "ability",
    "able",
    "about",
    "above",
    "accept",
    "according",
    "account",
    "across",
    "act",
    "action",
    "activity",
    "actually",
    "add",
    "address",
    "administration",
    "admit",
    "adult",
    "affect",
    "after",
    "again",
    "against",
    "age",
    "agency",
    "agent",
    "ago",
    "agree",
    "agreement",
    "ahead",
    "air",
    "all",
    "allow",
    "almost",
    "alone",
    "along",
    "already",
    "also",
    "although",
    "always",
    "American",
    "among",
    "amount",
    "analysis",
    "and",
    "animal",
    "another",
    "answer",
    "any",
    "anyone",
    "anything",
    "appear",
    "apply",
    "approach",
    "area",
    "argue",
    "arm",
    "around",
    "arrive",
    "art",
    "article",
    "artist",
    "ask",
    "assume",
    "attack",
    "attention",
    "attorney",
    "audience",
    "author",
    "authority",
    "available",
    "avoid",
    "away",
    "baby",
    "back",
    "bad",
    "bag",
    "ball",
    "bank",
    "bar",
    "base",
    "beat",
    "beautiful",
    "because",
    "become",
    "bed",
    "before",
    "begin",
    "behavior",
    "behind",
    "believe",
    "benefit",
    "best",
    "better",
    "between",
    "beyond",
    "big",
    "bill",
    "billion",
    "bit",
    "black",
    "blood",
    "blue",
    "board",
    "body",
    "book",
    "born",
    "both",
    "box",
    "boy",
    "break",
    "bring",
    "brother",
    "budget",
    "build",
    "building",
    "business",
    "but",
    "buy",
    "call",
    "camera",
    "campaign",
    "can",
    "cancer",
    "candidate",
    "capital",
    "car",
    "card",
    "care",
    "career",
    "carry",
    "case",
    "catch",
    "cause",
    "cell",
    "center",
    "central",
    "century",
    "certain",
    "certainly",
    "chair",
    "challenge",
    "chance",
    "change",
    "character",
    "charge",
    "check",
    "child",
    "choice",
    "choose",
    "church",
    "citizen",
    "city",
    "civil",
    "claim",
    "class",
    "clear",
    "clearly",
    "close",
    "coach",
    "cold",
    "collection",
    "college",
    "color",
    "come",
    "commercial",
    "common",
    "community",
    "company",
    "compare",
    "computer",
    "concern",
    "condition",
    "conference",
    "Congress",
    "consider",
    "consumer",
    "contain",
    "continue",
    "control",
    "cost",
    "could",
    "country",
    "couple",
    "course",
    "court",
    "cover",
    "create",
    "crime",
    "cultural",
    "culture",
    "cup",
    "current",
    "customer",
    "cut",
    "dark",
    "data",
    "daughter",
    "day",
    "dead",
    "deal",
    "death",
    "debate",
    "decade",
    "decide",
    "decision",
    "deep",
    "defense",
    "degree",
    "Democrat",
    "democratic",
    "describe",
    "design",
    "despite",
    "detail",
    "determine",
    "develop",
    "development",
    "die",
    "difference",
    "different",
    "difficult",
    "dinner",
    "direction",
    "director",
    "discover",
    "discuss",
    "discussion",
    "disease",
    "doctor",
    "dog",
    "door",
    "down",
    "draw",
    "dream",
    "drive",
    "drop",
    "drug",
    "during",
    "each",
    "early",
    "east",
    "easy",
    "eat",
    "economic",
    "economy",
    "edge",
    "education",
    "effect",
    "effort",
    "eight",
    "either",
    "election",
    "else",
    "employee",
    "end",
    "energy",
    "enjoy",
    "enough",
    "enter",
    "entire",
    "environment",
    "environmental",
    "especially",
    "establish",
    "even",
    "evening",
    "event",
    "ever",
    "every",
    "everybody",
    "everyone",
    "everything",
    "evidence",
    "exactly",
    "example",
    "executive",
    "exist",
    "expect",
    "experience",
    "expert",
    "explain",
    "face",
    "fact",
    "factor",
    "fail",
    "fall",
    "family",
    "far",
    "fast",
    "father",
    "fear",
    "federal",
    "feel",
    "feeling",
    "few",
    "field",
    "fight",
    "figure",
    "fill",
    "film",
    "final",
    "finally",
    "financial",
    "find",
    "fine",
    "finger",
    "finish",
    "fire",
    "firm",
    "first",
    "fish",
    "five",
    "floor",
    "fly",
    "focus",
    "follow",
    "food",
    "foot",
    "for",
    "force",
    "foreign",
    "forget",
    "form",
    "former",
    "forward",
    "four",
    "free",
    "friend",
    "from",
    "front",
    "full",
    "fund",
    "future",
    "game",
    "garden",
    "gas",
    "general",
    "generation",
    "get",
    "girl",
    "give",
    "glass",
    "goal",
    "good",
    "government",
    "great",
    "green",
    "ground",
    "group",
    "grow",
    "growth",
    "guess",
    "gun",
    "guy",
    "hair",
    "half",
    "hand",
    "hang",
    "happen",
    "happy",
    "hard",
    "have",
    "head",
    "health",
    "hear",
    "heart",
    "heat",
    "heavy",
    "help",
    "her",
    "here",
    "herself",
    "high",
    "him",
    "himself",
    "his",
    "history",
    "hit",
    "hold",
    "home",
    "hope",
    "hospital",
    "hot",
    "hotel",
    "hour",
    "house",
    "how",
    "however",
    "huge",
    "human",
    "hundred",
    "husband",
    "idea",
    "identify",
    "image",
    "imagine",
    "impact",
    "important",
    "improve",
    "include",
    "including",
    "increase",
    "indeed",
    "indicate",
    "individual",
    "industry",
    "information",
    "inside",
    "instead",
    "institution",
    "interest",
    "interesting",
    "international",
    "interview",
    "into",
    "investment",
    "involve",
    "issue",
    "item",
    "its",
    "itself",
    "job",
    "join",
    "just",
    "keep",
    "key",
    "kid",
    "kill",
    "kind",
    "kitchen",
    "know",
    "knowledge",
    "land",
    "language",
    "large",
    "last",
    "late",
    "later",
    "laugh",
    "law",
    "lawyer",
    "lay",
    "lead",
    "leader",
    "learn",
    "least",
    "leave",
    "left",
    "leg",
    "legal",
    "less",
    "let",
    "letter",
    "lie",
    "life",
    "light",
    "like",
    "likely",
    "line",
    "list",
    "listen",
    "little",
    "live",
    "local",
    "long",
    "look",
    "lose",
    "loss",
    "lot",
    "love",
    "low",
    "machine",
    "magazine",
    "main",
    "maintain",
    "major",
    "majority",
    "make",
    "man",
    "manage",
    "management",
    "manager",
    "many",
    "market",
    "marriage",
    "material",
    "matter",
    "may",
    "maybe",
    "mean",
    "measure",
    "media",
    "medical",
    "meet",
    "meeting",
    "member",
    "memory",
    "mention",
    "message",
    "method",
    "middle",
    "might",
    "military",
    "million",
    "mind",
    "minute",
    "miss",
    "mission",
    "model",
    "modern",
    "moment",
    "money",
    "month",
    "more",
    "morning",
    "most",
    "mother",
    "mouth",
    "move",
    "movement",
    "movie",
    "Mrs",
    "much",
    "music",
    "must",
    "myself",
    "name",
    "nation",
    "national",
    "natural",
    "nature",
    "near",
    "nearly",
    "necessary",
    "need",
    "network",
    "never",
    "new",
    "news",
    "newspaper",
    "next",
    "nice",
    "night",
    "none",
    "nor",
    "north",
    "not",
    "note",
    "nothing",
    "notice",
    "now",
    "n't",
    "number",
    "occur",
    "off",
    "offer",
    "office",
    "officer",
    "official",
    "often",
    "oil",
    "old",
    "once",
    "one",
    "only",
    "onto",
    "open",
    "operation",
    "opportunity",
    "option",
    "order",
    "organization",
    "other",
    "others",
    "our",
    "out",
    "outside",
    "over",
    "own",
    "owner",
    "page",
    "pain",
    "painting",
    "paper",
    "parent",
    "part",
    "participant",
    "particular",
    "particularly",
    "partner",
    "party",
    "pass",
    "past",
    "patient",
    "pattern",
    "pay",
    "peace",
    "people",
    "per",
    "perform",
    "performance",
    "perhaps",
    "period",
    "person",
    "personal",
    "phone",
    "physical",
    "pick",
    "picture",
    "piece",
    "place",
    "plan",
    "plant",
    "play",
    "player",
    "point",
    "police",
    "policy",
    "political",
    "politics",
    "poor",
    "popular",
    "population",
    "position",
    "positive",
    "possible",
    "power",
    "practice",
    "prepare",
    "present",
    "president",
    "pressure",
    "pretty",
    "prevent",
    "price",
    "private",
    "probably",
    "problem",
    "process",
    "produce",
    "product",
    "production",
    "professional",
    "professor",
    "program",
    "project",
    "property",
    "protect",
    "prove",
    "provide",
    "public",
    "pull",
    "purpose",
    "push",
    "put",
    "quality",
    "question",
    "quickly",
    "quite",
    "race",
    "radio",
    "raise",
    "range",
    "rate",
    "rather",
    "reach",
    "read",
    "ready",
    "real",
    "reality",
    "realize",
    "really",
    "reason",
    "receive",
    "recent",
    "recently",
    "recognize",
    "record",
    "red",
    "reduce",
    "reflect",
    "region",
    "relate",
    "relationship",
    "religious",
    "remain",
    "remember",
    "remove",
    "report",
    "represent",
    "Republican",
    "require",
    "research",
    "resource",
    "respond",
    "response",
    "responsibility",
    "rest",
    "result",
    "return",
    "reveal",
    "rich",
    "right",
    "rise",
    "risk",
    "road",
    "rock",
    "role",
    "room",
    "rule",
    "run",
    "safe",
    "same",
    "save",
    "say",
    "scene",
    "school",
    "science",
    "scientist",
    "score",
    "sea",
    "season",
    "seat",
    "second",
    "section",
    "security",
    "see",
    "seek",
    "seem",
    "sell",
    "send",
    "senior",
    "sense",
    "series",
    "serious",
    "serve",
    "service",
    "set",
    "seven",
    "several",
    "sex",
    "sexual",
    "shake",
    "share",
    "she",
    "shoot",
    "short",
    "shot",
    "should",
    "shoulder",
    "show",
    "side",
    "sign",
    "significant",
    "similar",
    "simple",
    "simply",
    "since",
    "sing",
    "single",
    "sister",
    "sit",
    "site",
    "situation",
    "six",
    "size",
    "skill",
    "skin",
    "small",
    "smile",
    "social",
    "society",
    "soldier",
    "some",
    "somebody",
    "someone",
    "something",
    "sometimes",
    "son",
    "song",
    "soon",
    "sort",
    "sound",
    "source",
    "south",
    "southern",
    "space",
    "speak",
    "special",
    "specific",
    "speech",
    "spend",
    "sport",
    "spring",
    "staff",
    "stage",
    "stand",
    "standard",
    "star",
    "start",
    "state",
    "statement",
    "station",
    "stay",
    "step",
    "still",
    "stock",
    "stop",
    "store",
    "story",
    "strategy",
    "street",
    "strong",
    "structure",
    "student",
    "study",
    "stuff",
    "style",
    "subject",
    "success",
    "successful",
    "such",
    "suddenly",
    "suffer",
    "suggest",
    "summer",
    "support",
    "sure",
    "surface",
    "system",
    "table",
    "take",
    "talk",
    "task",
    "tax",
    "teach",
    "teacher",
    "team",
    "technology",
    "television",
    "tell",
    "ten",
    "tend",
    "term",
    "test",
    "than",
    "thank",
    "that",
    "the",
    "their",
    "them",
    "themselves",
    "then",
    "theory",
    "there",
    "these",
    "they",
    "thing",
    "think",
    "third",
    "this",
    "those",
    "though",
    "thought",
    "thousand",
    "threat",
    "three",
    "through",
    "throughout",
    "throw",
    "thus",
    "time",
    "today",
    "together",
    "tonight",
    "too",
    "top",
    "total",
    "tough",
    "toward",
    "town",
    "trade",
    "traditional",
    "training",
    "travel",
    "treat",
    "treatment",
    "tree",
    "trial",
    "trip",
    "trouble",
    "true",
    "truth",
    "try",
    "turn",
    "two",
    "type",
    "under",
    "understand",
    "unit",
    "until",
    "upon",
    "use",
    "usually",
    "value",
    "various",
    "very",
    "victim",
    "view",
    "violence",
    "visit",
    "voice",
    "vote",
    "wait",
    "walk",
    "wall",
    "want",
    "war",
    "watch",
    "water",
    "way",
    "weapon",
    "wear",
    "week",
    "weight",
    "well",
    "west",
    "western",
    "what",
    "whatever",
    "when",
    "where",
    "whether",
    "which",
    "while",
    "white",
    "who",
    "whole",
    "whom",
    "whose",
    "why",
    "wide",
    "wife",
    "will",
    "win",
    "wind",
    "window",
    "wish",
    "with",
    "within",
    "without",
    "woman",
    "wonder",
    "word",
    "work",
    "worker",
    "world",
    "worry",
    "would",
    "write",
    "writer",
    "wrong",
    "yard",
    "yeah",
    "year",
    "yes",
    "yet",
    "you",
    "young",
    "your",
    "yourself",
]
