from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import datetime
from typing import Sequence

from . import WordSearch, __app_name__, __version__, config, utils
from .mask import shapes
from .mask.bitmap import Image
from .word import Direction

BUILTIN_SHAPES = shapes.get_shape_objects()


class RandomAction(argparse.Action):
    """Restrict argparse `-r`, `--random` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = config.min_puzzle_words
        max_val = config.max_puzzle_words
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
({', '.join([str(i) for i in config.level_dirs.keys()])}) or accepted \
cardinal directions ({', '.join([d.name for d in Direction])})."
                    )
            setattr(namespace, self.dest, values)


class SizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = config.min_puzzle_size
        max_val = config.max_puzzle_size
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


Valid Levels: {', '.join([str(i) for i in config.level_dirs.keys()])}
Valid Directions: {', '.join([d.name for d in Direction])}
* Directions are to be provided as a comma-separated list.""",
        epilog="Copyright 2022 Josh Duncan (joshbduncan.com)",
        prog=__app_name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    words_group = parser.add_mutually_exclusive_group()
    secret_words_group = parser.add_mutually_exclusive_group()
    mask_group = parser.add_mutually_exclusive_group()
    words_group.add_argument(
        "words",
        type=str,
        nargs="*",
        default=sys.stdin,
        help="Words to include in the puzzle (default: stdin).",
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
        choices=BUILTIN_SHAPES,
        metavar="MASK_SHAPE",
        help=f"Mask the puzzle to a shape \
(choices: {', '.join(BUILTIN_SHAPES)}).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output path for the saved puzzle.",
    )
    parser.add_argument(
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
        help=f"{config.min_puzzle_size} <= puzzle size <= {config.max_puzzle_size}",
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
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args(argv)

    # check for mask preview first
    if args.preview_masks:
        preview_size = 21
        for shape in BUILTIN_SHAPES:
            mask = eval(f"shapes.{shape}")()
            mask.generate(preview_size)
            print(f"{shape}")
            mask.show(True)
            print()
        return 0

    # process puzzle words
    words = ""
    if args.random:
        words = ",".join(utils.get_random_words(args.random))
    else:
        if isinstance(args.words, list):
            # needed when words were provided as "command, then, space"
            words = ",".join([word.replace(",", "") for word in args.words])
        elif not sys.stdin.isatty():
            # disable interactive tty which can be confusing
            # but still process words were piped in from the shell
            words = args.words.read().rstrip()

    # process secret puzzle words
    secret_words = (
        args.secret_words
        if args.secret_words
        else ",".join(utils.get_random_words(args.random_secret_words))
        if args.random_secret_words
        else ""
    )

    # if not words were found exit the script
    if not words and not secret_words:
        print("No words provided. Learn more with the '-h' flag.", file=sys.stderr)
        return 1

    # create a new puzzle object from provided arguments
    puzzle = WordSearch(
        words,
        level=args.difficulty,
        size=args.size,
        secret_words=secret_words if secret_words else None,
        secret_level=args.secret_difficulty,
    )

    # apply masking is specified
    if args.mask:
        puzzle.apply_mask(eval(f"shapes.{args.mask}")())
    if args.image_mask:
        puzzle.apply_mask(Image(args.image_mask))

    # show the result
    if args.output or args.format:
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
