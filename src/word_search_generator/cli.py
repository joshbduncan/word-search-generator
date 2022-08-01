import argparse
import pathlib
import sys
from typing import Optional, Sequence

from word_search_generator import WordSearch, __app_name__, __version__, config, utils


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


def main(
    argv: Optional[Sequence[str]] = None, prog: Optional[str] = __app_name__
) -> int:
    """Word Search Generator CLI.

    Args:
        argv (Optional[Sequence[str]], optional): Command line arguments.
        Defaults to None.
        prog (Optional[str], optional): Program name. Defaults to __app_name__.

    Returns:
        int: Exit status.
    """
    # setup argparse to capture cli arguments
    parser = argparse.ArgumentParser(
        description=f"Generate Word Search Puzzles! (Version {__version__})",
        epilog="Copyright 2022 Josh Duncan (joshd.xyz)",
        prog=prog,
    )
    # define all possible arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "words",
        type=str,
        nargs="*",
        default=sys.stdin,
        help="Words to include in the puzzle",
    )
    group.add_argument(
        "-r",
        "--random",
        type=int,
        action=RandomAction,
        help="Generate {n} random words to include in the puzzle",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=[1, 2, 3],
        help="Difficulty level (1) beginner, (2) intermediate, (3) expert",
    )
    parser.add_argument(
        "-s",
        "--size",
        action=SizeAction,
        type=int,
        help=f"Puzzle size >={config.min_puzzle_size} and <={config.max_puzzle_size}",
    )
    parser.add_argument(
        "-c",
        "--cheat",
        action=argparse.BooleanOptionalAction,
        help="Highlight all hidden puzzle words.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output path for saved puzzle. Specify export type by appending "
        "'.pdf' or '.csv' to your path (defaults to PDF)",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # capture all cli arguments and make sure words were provided
    args = parser.parse_args()

    # check if random words were requested
    if args.random:
        words = utils.get_random_words(args.random)
    else:
        words = ",".join(args.words)

    # check to see if solution should be highlighted
    cheat = True if args.cheat else False

    # create a new puzzle object from provided arguments
    puzzle = WordSearch(words, level=args.level, size=args.size)
    # show the result
    if args.output:
        foutput = puzzle.save(path=args.output)
        print(f"Puzzle saved: {foutput}")
    else:
        puzzle.show(solution=cheat)

    return 0


if __name__ == "__main__":
    sys.exit(main())
