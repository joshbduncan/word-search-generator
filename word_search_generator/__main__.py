import argparse
import pathlib

from . import WordSearch
from . import utils


class MinSizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` value to >=10."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values < 10:
            parser.error("minimum size for {0} is 10".format(option_string))
        setattr(namespace, self.dest, values)


def cli():
    # setup argparse to capture cli arguments
    parser = argparse.ArgumentParser(
        description="Generate Word Search Puzzles!",
        epilog="Copyright 2021 Josh Duncan (joshbduncan.com)",
    )
    # define all possible arguments
    parser.add_argument("-w", "--words", nargs="+", help="words to hide in the puzzle")
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
        "-p",
        "--path",
        help="export path for '-e', '--export' flag",
        type=pathlib.Path,
    )

    # capture all cli arguments and make sure words were provided
    args = parser.parse_args()
    if not args.words:
        parser.error(
            "You must provide a list of words. Use '-h' or '--help' for more info.\n"
        )
    # if export flag make sure output path was specified
    if args.export and args.path is None:
        parser.error("-e, --export requires -p, --path.")

    # create a new puzzle object from provided arguments
    puzzle = WordSearch(",".join(args.words), level=args.level, size=args.size)
    # show the result
    if args.export:
        exported_file = puzzle.save(
            path=args.path.absolute(), format=args.export.upper()
        )
        print(f"Puzzle saved: {exported_file}")
    else:
        puzzle.show(key=args.key, tabs=args.tabs)


if __name__ == "__main__":
    cli()
