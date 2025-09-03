import argparse
import sys
from collections.abc import ItemsView, Sequence
from importlib.metadata import version
from pathlib import Path

from .core.directions import LEVEL_DIRS
from .core.formatter import ExportFormat
from .core.word import Direction
from .mask import ImageMask, Mask, shapes
from .utils import get_random_words
from .word_search import WordSearch
from .words import WORD_LISTS

BUILTIN_MASK_SHAPES: dict[str, type[Mask]] = shapes.get_shape_objects()


class PrintExamples(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        formatter = parser._get_formatter()  # gets your RawDescriptionHelpFormatter
        formatter.add_text(parser.epilog)
        print(formatter.format_help())  # only prints the epilog part
        parser.exit()


class RandomAction(argparse.Action):
    """Restrict argparse `-r`, `--random` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = WordSearch.MIN_PUZZLE_WORDS
        max_val = WordSearch.MAX_PUZZLE_WORDS
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
                        f"{option_string} must be either numeric levels "
                        f"({', '.join([str(i) for i in LEVEL_DIRS])}) or accepted "
                        f"cardinal directions "
                        f"({', '.join([d.name for d in Direction])})."
                    )
            setattr(namespace, self.dest, values)


class SizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = WordSearch.MIN_PUZZLE_SIZE
        max_val = WordSearch.MAX_PUZZLE_SIZE
        if values < min_val or values > max_val:
            parser.error(f"{option_string} must be >={min_val} and <={max_val}")
        setattr(namespace, self.dest, values)


def create_parser() -> argparse.ArgumentParser:
    examples = """\
examples:
  %(prog)s animals,tiger,shark -s 15
  %(prog)s --random 30 --theme animals --cheat -f PDF -o puzzle.pdf
  %(prog)s -i words.txt --size 20 --mask star5
  %(prog)s --random 25 --theme coastal --secret-words wave,sand
  %(prog)s --random 30 --theme automotive --difficulty 4 --cheat
  %(prog)s --random 30 --theme sports --difficulty N,E,SW
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""Generate Word Search Puzzles! \


Valid Levels: {", ".join([str(i) for i in LEVEL_DIRS])}
Valid Directions: {", ".join([d.name for d in Direction])}
* Directions are to be provided as a comma-separated list.""",
    )
    words_group = parser.add_mutually_exclusive_group()
    secret_words_group = parser.add_mutually_exclusive_group()
    preview_group = parser.add_mutually_exclusive_group()
    mask_group = parser.add_mutually_exclusive_group()
    sort_group = parser.add_mutually_exclusive_group()
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
        type=Path,
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
        "--examples",
        nargs=0,
        action=PrintExamples,
        help="Show extended usage examples and exit.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "json", "pdf"],
        type=str.lower,
        metavar="EXPORT_FORMAT",
        help='Puzzle output format \
(choices: "csv", "json", "pdf").',
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
        type=Path,
        help="Mask the puzzle to a provided image \
(accepts: BMP, JPEG, PNG).",
    )
    mask_group.add_argument(
        "-m",
        "--mask",
        choices=BUILTIN_MASK_SHAPES,
        type=str.lower,
        metavar="MASK_SHAPE",
        help=f"Mask the puzzle to a shape \
(choices: {', '.join(sorted(BUILTIN_MASK_SHAPES.keys()))}).",
    )
    parser.add_argument(
        "--no-validators",
        action="store_true",
        help="Disable default word validators.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for the saved puzzle.",
    )
    preview_group.add_argument(
        "-pm",
        "--preview-masks",
        nargs="?",  # 0 or 1 values
        const="*",  # if no value given, set to "*"
        type=str.lower,
        metavar="MASK",
        help="Preview a mask shape (give MASK), or all masks if none is provided.",
    )
    preview_group.add_argument(
        "-pt",
        "--preview-themes",
        nargs="?",  # 0 or 1 values
        const="*",  # if no value given, set to "*"
        type=str.lower,
        metavar="THEME",
        help="Preview a theme word list (give THEME), \
or all word lists if none is provided.",
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
If all words can't be placed, an exception will be raised.",
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
        help=f"{WordSearch.MIN_PUZZLE_SIZE} <= size <= {WordSearch.MAX_PUZZLE_SIZE}",
    )
    parser.add_argument(
        "--theme",
        choices=WORD_LISTS.keys(),
        type=str.lower,
        metavar="THEME",
        help=f"Pick random words from a themed word list \
(choices: {', '.join(sorted(WORD_LISTS.keys()))}). Requires --random.",
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
    sort_group.add_argument(
        "--sort-words",
        dest="sort_words",
        action="store_true",
        help="Sort word list and answer key alphabetically in output (default: true).",
    )
    sort_group.add_argument(
        "--no-sort-words",
        dest="sort_words",
        action="store_false",
        help="Maintain original word order for word list and answer key in output.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('word_search_generator')}",
    )
    parser.set_defaults(sort_words=True)
    return parser


def preview_masks(
    masks: list[tuple[str, type[Mask]]] | ItemsView[str, type[Mask]] | None = None,
) -> None:
    from rich import box
    from rich.table import Table

    from .console import console

    preview_size: int = 21

    if masks is None:
        masks = BUILTIN_MASK_SHAPES.items()

    for name, shape in masks:
        mask: Mask = shape()
        mask.generate(preview_size)
        table = Table(
            title=name.upper(),
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
            table.add_column(width=1, justify="center", vertical="middle", no_wrap=True)

        for row in mask.mask[min_y : max_y + 1]:
            table.add_row(*[c if c == mask.ACTIVE else " " for c in row])

        console.print(table)


def preview_themes(
    themes: list[tuple[str, list[str]]] | ItemsView[str, list[str]] | None = None,
) -> None:
    if themes is None:
        themes = WORD_LISTS.items()

    for name, word_list in themes:
        print(f"{name.upper()}:")
        print(", ".join(word_list))
        print("")


def process_words(args: argparse.Namespace) -> str:
    words: str = ""
    if args.random:
        word_list: list[str] = (
            WORD_LISTS.get(args.theme, WORD_LISTS["dictionary"])
            if args.theme
            else WORD_LISTS["dictionary"]
        )
        words = get_random_words(
            args.random,
            max_length=args.size if args.size else None,
            word_list=word_list,
        )
    elif args.input:
        words = args.input.read_text()
    elif isinstance(args.words, list) and args.words:
        if len(args.words) == 1 and "," in args.words[0]:
            words = ",".join(w.strip() for w in args.words[0].split(","))
        else:
            words = ",".join(word.replace(",", "") for word in args.words)
    elif not sys.stdin.isatty():
        # disable interactive tty which can be confusing
        # but still process words were piped in from the shell
        words = args.words.read().rstrip()
    return words


def process_secret_words(args: argparse.Namespace) -> str:
    secret_words = ""
    if args.secret_words:
        secret_words = args.secret_words
    elif args.random_secret_words:
        secret_words = get_random_words(args.random_secret_words)
    return secret_words


def main(argv: Sequence[str] | None = None) -> int:
    """Word Search Generator CLI.

    Args:
        argv (Sequence[str] | None, optional): Command line arguments. Defaults to None.

    Returns:
        int: Exit status.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # dependency: --random-from requires --random
    if args.theme and not args.random:
        parser.error("--theme requires --random N")

    # check for mask preview first
    if args.preview_masks:
        if args.preview_masks == "*":  # no arg given
            masks = None
        else:
            try:
                preview_mask: type[Mask] = BUILTIN_MASK_SHAPES[args.preview_masks]
                masks = [(args.preview_masks, preview_mask)]
            except KeyError:
                parser.error(
                    f"Mask '{args.preview_masks}' not found. "
                    f"Valid choices: {', '.join(sorted(BUILTIN_MASK_SHAPES))}"
                )
        preview_masks(masks)
        parser.exit()

    # check for theme preview second
    if args.preview_themes:
        if args.preview_themes == "*":  # no arg given
            themes = None
        else:
            try:
                theme: list[str] = WORD_LISTS[args.preview_themes]
                themes = [(args.preview_themes, theme)]
            except KeyError:
                parser.error(
                    f"Theme '{args.preview_themes}' not found. "
                    f"Valid choices: {', '.join(sorted(WORD_LISTS.keys()))}"
                )
        preview_themes(themes)
        parser.exit()

    # process puzzle words
    words = process_words(args)

    # process secret puzzle words
    secret_words = process_secret_words(args)

    # if no words were found exit the script
    if not words and not secret_words:
        print("No words provided. Learn more with the '-h' flag.", file=sys.stderr)
        return 1

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
        mask_class: type[Mask] = BUILTIN_MASK_SHAPES[args.mask]
        mask: Mask = mask_class()

        if mask.min_size is not None and not args.size and puzzle.size < mask.min_size:
            puzzle.size = mask.min_size

        puzzle.apply_mask(mask)

    if args.image_mask:
        puzzle.apply_mask(ImageMask(args.image_mask))

    # show the result
    if args.output or args.format:
        from datetime import datetime

        # Convert string format to ExportFormat enum
        if args.format:
            format = ExportFormat.from_string(args.format)
        else:
            format = ExportFormat.PDF
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(":", "")
        path = (
            args.output
            if args.output
            else f"WordSearchPuzzle {timestamp}.{str(format).lower()}"
        )
        foutput = puzzle.save(
            path=path,
            format=format,
            solution=args.cheat,
            lowercase=args.lowercase,
            hide_key=args.hide_key,
            sort_word_list=args.sort_words,
        )
        print(f"Puzzle saved: {foutput}")

    else:
        puzzle.show(
            solution=args.cheat,
            lowercase=args.lowercase,
            hide_key=args.hide_key,
            reversed_letters=not args.cheat,
            sort_word_list=args.sort_words,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
