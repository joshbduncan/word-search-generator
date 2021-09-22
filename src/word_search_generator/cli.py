import argparse
import pathlib
import sys

from word_search_generator import WordSearch
from word_search_generator import config
from word_search_generator import utils


class RandomAction(argparse.Action):
    """Restrict argparse `-r`, `--random` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = config.min_puzzle_words
        max_val = config.max_puzzle_words
        if values < min_val or values > max_val:
            parser.error(f"{option_string} must be >={min_val} and <={max_val}")
        setattr(namespace, self.dest, values)


class SizeAction(argparse.Action):
    """Restrict argparse `-s`, `--size` inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        min_val = config.min_puzzle_size
        max_val = config.max_puzzle_size
        if values < min_val or values > max_val:
            parser.error(f"{option_string} must be >={min_val} and <={max_val}")
        setattr(namespace, self.dest, values)


def main():
    """Word Search Generator CLI"""

    # setup argparse to capture cli arguments
    parser = argparse.ArgumentParser(
        description="Generate Word Search Puzzles!",
        epilog="Copyright 2021 Josh Duncan (joshbduncan.com)",
    )
    # define all possible arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "words",
        type=str,
        nargs="*",
        default=sys.stdin,
        help="words to include in the puzzle",
    )
    group.add_argument(
        "-r",
        "--random",
        type=int,
        action=RandomAction,
        help="difficulty level (1) beginner, (2) intermediate, (3) expert",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=[1, 2, 3],
        help="difficulty level (1) beginner, (2) intermediate, (3) expert",
    )
    parser.add_argument(
        "-s",
        "--size",
        action=SizeAction,
        type=int,
        help=f"puzzle size >={config.min_puzzle_size} and <={config.max_puzzle_size}",
    )
    parser.add_argument("-k", "--key", help="show answer key", action="store_true")
    parser.add_argument(
        "-t", "--tabs", help="use tabs as character separator", action="store_true"
    )
    parser.add_argument(
        "-e",
        "--export",
        choices=["csv", "pdf"],
        help="export puzzle as 'csv' or 'pdf' file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="output path for '-e', '--export' flag",
    )

    # capture all cli arguments and make sure words were provided
    args = parser.parse_args()

    # check if random words were requested
    if args.random:
        words = utils.get_random_words(args.random)
    else:
        words = ",".join(args.words)

    # create a new puzzle object from provided arguments
    puzzle = WordSearch(words, level=args.level, size=args.size)
    # show the result
    if args.export:
        fexport = puzzle.save(path=args.output, format=args.export.upper())
        print(f"Puzzle saved: {fexport}")
    else:
        puzzle.show(key=args.key, tabs=args.tabs)
