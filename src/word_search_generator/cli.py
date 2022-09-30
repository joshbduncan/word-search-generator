import argparse
import pathlib
import sys
from typing import Sequence

from word_search_generator import WordSearch, config, utils


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
    argv: Sequence[str] | None = None,
    prog: str | None = None,
    version: str | None = None,
) -> int:
    """Word Search Generator CLI.

    Args:
        argv (Sequence[str] | None, optional): Command line arguments. Defaults to None.
        prog (str | None, optional): Program name. Defaults to None.
        version (str | None, optional): Program version. Defaults to None.

    Returns:
        int: Exit status.
    """

    # setup argparse to capture cli arguments
    parser = argparse.ArgumentParser(
        description="Generate Word Search Puzzles!",
        epilog="Copyright 2022 Josh Duncan (joshbduncan.com)",
        prog=prog,
    )
    # define all possible arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "words",
        type=str,
        nargs="*",
        default=sys.stdin,
        help="Words to include in the puzzle (default: stdin).",
    )
    group.add_argument(
        "-r",
        "--random",
        type=int,
        action=RandomAction,
        help="Generate {n} random words to include in the puzzle.",
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
        action="store_true",
        help="Show the puzzle solution or include it within the `-o, --output` file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output path for saved puzzle. Specify export type by appending "
        "'.pdf' or '.csv' to your path (default: %(default)s)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")

    # capture all cli arguments and make sure words were provided
    args = parser.parse_args(argv)

    words = ""
    # check if random words were requested
    if args.random:
        words = utils.get_random_words(args.random)
    else:
        if isinstance(args.words, list):
            words = ",".join(args.words)
        elif not sys.stdin.isatty():
            # disable interactive tty which can be confusing
            # but still process words were piped in from the shell
            words = args.words.read().rstrip()

    # if not words were found exit the script
    if not words:
        print("No words provided. Learn more with the '-h' flag.", file=sys.stderr)
        return 1

    # create a new puzzle object from provided arguments
    puzzle = WordSearch(words, level=args.level, size=args.size)
    # show the result
    if args.output:
        foutput = puzzle.save(path=args.output, solution=args.cheat)
        print(f"Puzzle saved: {foutput}")
    else:
        puzzle.show(solution=args.cheat)

    return 0


if __name__ == "__main__":
    sys.exit(main())
