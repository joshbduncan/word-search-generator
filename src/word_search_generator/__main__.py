from word_search_generator import __app_name__, __version__, cli


def main():
    cli.main(prog=__app_name__, version=__version__)


if __name__ == "__main__":
    """WordSearch CLI access point."""
    main()
