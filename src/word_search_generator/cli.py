import argparse
import pathlib
import sys
from importlib.metadata import version
from typing import Sequence

from .config import (
    level_dirs,
    max_puzzle_size,
    max_puzzle_words,
    min_puzzle_size,
    min_puzzle_words,
)
from .mask import shapes
from .utils import get_random_words
from .word import Direction

BUILTIN_MASK_SHAPES_OBJECTS = shapes.get_shape_objects()


class RandomAction(argparse.Action):
    """Restrict argparse `-r`, `--random` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = min_puzzle_words
        max_val = max_puzzle_words
        if values < min_val or values > max_val:
            parser.error(f"{option_string} must be >={min_val} and <={max_val}")
        setattr(namespace, self.dest, values)


class DifficultyAction(argparse.Action):
    """Validate difficulty level integers or directional strings."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values.isnumeric():
            setattr(namespace, self.dest, int(values))
        else:
            for d in values.split(","):
                if d.strip().isnumeric():
                    parser.error(
                        f"{option_string} must be \
either numeric levels \
({', '.join([str(i) for i in level_dirs])}) or accepted \
cardinal directions ({', '.join([d.name for d in Direction])})."
                    )
            setattr(namespace, self.dest, values)


class SizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = min_puzzle_size
        max_val = max_puzzle_size
        if values < min_val or values > max_val:
            parser.error(f"{option_string} must be >={min_val} and <={max_val}")
        setattr(namespace, self.dest, values)


def main(argv: Sequence[str] | None = None) -> int:
    """Word Search Generator CLI.

    Args:
        argv (Sequence[str] | None, optional): Command line arguments. Defaults to None.

    Returns:
        int: Exit status.
    """
    parser = argparse.ArgumentParser(
        description=f"""Generate Word Search Puzzles! \


Valid Levels: {', '.join([str(i) for i in level_dirs])}
Valid Directions: {', '.join([d.name for d in Direction])}
* Directions are to be provided as a comma-separated list.""",
        epilog="Copyright 2023 Josh Duncan (joshbduncan.com)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    words_group = parser.add_mutually_exclusive_group()
    secret_words_group = parser.add_mutually_exclusive_group()
    mask_group = parser.add_mutually_exclusive_group()
    play_group = parser.add_mutually_exclusive_group()
    words_group.add_argument(
        "words",
        type=str,
        nargs="*",
        default="",
        help="Words to include in the puzzle.",
    )
    words_group.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        help="Text file to load puzzle words from.",
    )
    parser.add_argument(
        "-c",
        "--cheat",
        action="store_true",
        help="Show the puzzle solution or include it within the `-o, --output` file.",
    )
    # new implementation of -l, --level allowing for more flexibility
    # keeping -l, --level for backwards compatibility
    parser.add_argument(
        "-d",
        "--difficulty",
        "-l",
        "--level",
        action=DifficultyAction,
        help="Difficulty level (numeric) or cardinal directions \
puzzle words can go. See valid arguments above.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["CSV", "JSON", "PDF", "csv", "json", "pdf"],
        metavar="EXPORT_FORMAT",
        help='Puzzle output format \
(choices: "CSV", "JSON", "PDF").',
    )
    mask_group.add_argument(
        "-im",
        "--image-mask",
        type=pathlib.Path,
        help="Mask the puzzle to a provided image \
(accepts: BMP, JPEG, PNG).",
    )
    mask_group.add_argument(
        "-m",
        "--mask",
        choices=BUILTIN_MASK_SHAPES_OBJECTS,
        metavar="MASK_SHAPE",
        help=f"Mask the puzzle to a shape \
(choices: {', '.join(BUILTIN_MASK_SHAPES_OBJECTS)}).",
    )
    parser.add_argument(
        "--no-validators",
        action="store_true",
        help="Disable default word validators.",
    )
    play_group.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output path for the saved puzzle.",
    )
    play_group.add_argument(
        "-p",
        "--play",
        action="store_true",
        help="Play a TUI version of a WordSearch. Requires \
            optional dependencies. Install using `pip install \
                word-search-generator[play]`.",
    )
    play_group.add_argument(
        "-pm",
        "--preview-masks",
        action="store_true",
        help="Preview all built-in mask shapes.",
    )
    words_group.add_argument(
        "-r",
        "--random",
        type=int,
        action=RandomAction,
        help="Generate {n} random words to include in the puzzle.",
    )
    secret_words_group.add_argument(
        "-rx",
        "--random-secret-words",
        type=int,
        action=RandomAction,
        help="Generate {n} random secret words to include in the puzzle.",
    )
    parser.add_argument(
        "-s",
        "--size",
        action=SizeAction,
        type=int,
        help=f"{min_puzzle_size} <= puzzle size <= {max_puzzle_size}",
    )
    secret_words_group.add_argument(
        "-x",
        "--secret-words",
        type=str,
        default="",
        help="Secret bonus words not included in the word list.",
    )
    parser.add_argument(
        "-xd",
        "--secret-difficulty",
        action=DifficultyAction,
        help="Difficulty level (numeric) or cardinal directions \
secret puzzle words can go. See valid arguments above.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('word_search_generator')}",
    )
    args = parser.parse_args(argv)

    # check for mask preview first
    if args.preview_masks:
        preview_size = 21
        for shape in BUILTIN_MASK_SHAPES_OBJECTS:
            mask = eval(f"shapes.{shape}")()
            mask.generate(preview_size)
            print(f"{shape}")
            mask.show(True)
            print()
        return 0

    # process puzzle words
    words = ""
    if args.random:
        words = ",".join(
            get_random_words(args.random, max_length=args.size if args.size else None)
        )
    elif args.input:
        words = args.input.read_text()
    else:
        if isinstance(args.words, list):
            # needed when words were provided as "command, then, space"
            words = ",".join([word.replace(",", "") for word in args.words])

    # process secret puzzle words
    secret_words = (
        args.secret_words
        if args.secret_words
        else ",".join(get_random_words(args.random_secret_words))
        if args.random_secret_words
        else ""
    )

    # if not words were found exit the script
    if not words and not secret_words:
        print("No words provided. Learn more with the '-h' flag.", file=sys.stderr)
        return 1

    # create a new puzzle object from provided arguments
    from .game.word_search import WordSearch

    puzzle = WordSearch(
        words,
        level=args.difficulty,
        size=args.size,
        secret_words=secret_words if secret_words else None,
        secret_level=args.secret_difficulty,
        validators=[] if args.no_validators else WordSearch.DEFAULT_VALIDATORS,
    )

    # apply masking if specified
    if args.mask:
        mask = eval(f"shapes.{args.mask}")()
        if hasattr(mask, "min_size") and not args.size and puzzle.size < mask.min_size:
            puzzle.size = mask.min_size
        puzzle.apply_mask(mask)

    if args.image_mask:
        from .mask.bitmap import Image

        puzzle.apply_mask(Image(args.image_mask))

    if args.play:
        from .tui.word_search import TUIGame

        app = TUIGame(puzzle)
        return app.run()  # type: ignore[return-value, no-any-return]

    # show the result
    elif args.output or args.format:
        from datetime import datetime

        format = args.format if args.format else "PDF"
        path = (
            args.output
            if args.output
            else f"WordSearchPuzzle {datetime.now()}.{format.lower()}"
        )
        foutput = puzzle.save(path=path, format=format, solution=args.cheat)
        print(f"Puzzle saved: {foutput}")

    else:
        puzzle.show(solution=args.cheat)

    return 0


if __name__ == "__main__":
    sys.exit(main())
