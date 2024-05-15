import argparse
import pathlib
import sys
from importlib.metadata import version
from typing import Sequence

from .core.directions import LEVEL_DIRS
from .core.game import Game
from .core.word import Direction
from .mask import Mask, shapes
from .utils import get_random_words

BUILTIN_MASK_SHAPES_OBJECTS = shapes.get_shape_objects()


class RandomAction(argparse.Action):
    """Restrict argparse `-r`, `--random` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = Game.MIN_PUZZLE_WORDS
        max_val = Game.MAX_PUZZLE_WORDS
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
({', '.join([str(i) for i in LEVEL_DIRS])}) or accepted \
cardinal directions ({', '.join([d.name for d in Direction])})."
                    )
            setattr(namespace, self.dest, values)


class SizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = Game.MIN_PUZZLE_SIZE
        max_val = Game.MAX_PUZZLE_SIZE
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


Valid Levels: {', '.join([str(i) for i in LEVEL_DIRS])}
Valid Directions: {', '.join([d.name for d in Direction])}
* Directions are to be provided as a comma-separated list.""",
        epilog="Copyright 2024 Josh Duncan (joshbduncan.com)",
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
    parser.add_argument(
        "-hk",
        "--hide-key",
        action="store_true",
        help="Hide the answer key from output.",
    )
    parser.add_argument(
        "-lc",
        "--lowercase",
        action="store_true",
        help="Output puzzle letters in lower (as opposed to the UPPERCASE default).",
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
    parser.add_argument(
        "-rall",
        "--require-all-words",
        action="store_true",
        help="Require all words to be placed by the generator. \
If all words can't be placed, and exception will be raised.",
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
        help=f"{Game.MIN_PUZZLE_SIZE} <= puzzle size <= {Game.MIN_PUZZLE_SIZE}",
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
        from rich import box
        from rich.table import Table

        from .console import console

        preview_size = 21

        for shape in BUILTIN_MASK_SHAPES_OBJECTS:
            mask: Mask = eval(f"shapes.{shape}")()
            mask.generate(preview_size)
            table = Table(
                title=shape,
                title_style="bold italic green",
                box=box.SIMPLE_HEAD,
                padding=0,
                show_edge=True,
                show_header=False,
                show_lines=False,
            )

            assert mask.bounding_box
            min_x, min_y = mask.bounding_box[0]
            max_x, max_y = mask.bounding_box[1]

            for _ in range(max_x - min_x + 1):
                table.add_column(
                    width=1, justify="center", vertical="middle", no_wrap=True
                )

            for row in mask.mask[min_y : max_y + 1]:
                table.add_row(*[c if c == mask.ACTIVE else " " for c in row])

            console.print(table)
        return 0

    # process puzzle words
    words = ""
    if args.random:
        words = ",".join(
            get_random_words(args.random, max_length=args.size if args.size else None)
        )
    elif args.input:
        words = args.input.read_text()
    elif isinstance(args.words, list):
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
        else (
            ",".join(utils.get_random_words(args.random_secret_words))
            if args.random_secret_words
            else ""
        )
    )

    # if not words were found exit the script
    if not words and not secret_words:
        print("No words provided. Learn more with the '-h' flag.", file=sys.stderr)
        return 1

    # create a new puzzle object from provided arguments
    from .word_search import WordSearch

    puzzle = WordSearch(
        words,
        level=args.difficulty,
        size=args.size,
        secret_words=secret_words if secret_words else None,
        secret_level=args.secret_difficulty,
        require_all_words=args.require_all_words,
        validators=None if args.no_validators else WordSearch.DEFAULT_VALIDATORS,
    )

    # apply masking if specified
    if args.mask:
        mask = eval(f"shapes.{args.mask}")()
        if hasattr(mask, "min_size") and not args.size and puzzle.size < mask.min_size:
            puzzle.size = mask.min_size
        puzzle.apply_mask(mask)

    if args.image_mask:
        from .mask.bitmap import BitmapImage

        puzzle.apply_mask(BitmapImage(args.image_mask))

    # show the result
    if args.output or args.format:
        from datetime import datetime

        format = args.format if args.format else "PDF"
        path = (
            args.output
            if args.output
            else f"WordSearchPuzzle {datetime.now()}.{format.lower()}"
        )
        foutput = puzzle.save(
            path=path,
            format=format,
            solution=args.cheat,
            lowercase=args.lowercase,
            hide_key=args.hide_key,
        )
        print(f"Puzzle saved: {foutput}")

    else:
        puzzle.show(
            solution=args.cheat,
            lowercase=args.lowercase,
            reversed_letters=not args.cheat,
            hide_key=args.hide_key,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
