import argparse
import pathlib
import sys

from . import WordSearch


class MinSizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` value to >=10."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values < 10:
            parser.error("minimum size for {0} is 10".format(option_string))
        setattr(namespace, self.dest, values)


def cli():
    """Word Search Generator CLI"""

    # setup argparse to capture cli arguments
    parser = argparse.ArgumentParser(
        description="Generate Word Search Puzzles!",
        epilog="Copyright 2021 Josh Duncan (joshbduncan.com)",
    )
    # define all possible arguments
    parser.add_argument(
        "words",
        type=str,
        nargs="*",
        help="words to include in the puzzle",
        default=sys.stdin,
    )
    parser.add_argument(
        "-l",
        "--level",
        help="difficulty level (1) beginner, (2) intermediate, (3) expert",
        type=int,
        choices=[1, 2, 3],
    )
    parser.add_argument(
        "-s", "--size", help="puzzle size >=10", action=MinSizeAction, type=int
    )
    parser.add_argument("-k", "--key", help="show answer key", action="store_true")
    parser.add_argument(
        "-t", "--tabs", help="use tabs as character separator", action="store_true"
    )
    parser.add_argument(
        "-e",
        "--export",
        help="export puzzle as 'csv' or 'pdf' file",
        choices=["csv", "pdf"],
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output path for '-e', '--export' flag",
        type=pathlib.Path,
    )

    # capture all cli arguments and make sure words were provided
    args = parser.parse_args()
    # create a new puzzle object from provided arguments
    puzzle = WordSearch(",".join(args.words), level=args.level, size=args.size)
    # show the result
    if args.export:
        fexport = puzzle.save(path=args.output, format=args.export.upper())
        print(f"Puzzle saved: {fexport}")
    else:
        puzzle.show(key=args.key, tabs=args.tabs)


if __name__ == "__main__":
    cli()
