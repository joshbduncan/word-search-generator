# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2023-05-02

### Added

- New pre-built mask shapes: [Club](https://github.com/joshbduncan/word-search-generator/wiki/Pre-Built-Mask-Shapes#Club), [Fish](https://github.com/joshbduncan/word-search-generator/wiki/Pre-Built-Mask-Shapes#Fish), [Flower](https://github.com/joshbduncan/word-search-generator/wiki/Pre-Built-Mask-Shapes#Flower), and [Spade](https://github.com/joshbduncan/word-search-generator/wiki/Pre-Built-Mask-Shapes#Spade)
- Testing for built-in masks shapes based on known output
- 'tools/build_masks_output_dict.py' tool for generating known built-in shapes output dict for us in testing

### Fixed

- During mask generation, each class and subclass now refers to their own `build_mask()` method instead of the base class.
- Incorrect horizontal center calculation for `Spade` and `Club` masks on even sized masks.

### Changed

- The `.random_words()` method default to **NOT** resetting the puzzle size.
- Radius calculation for the `RegularPolygon` mask.
- If the `random_words()` method is called on an empty `WordSearch()` object, an appropriate puzzle size is calculated.
- Cleaned up variable naming a bit to make things clear
    - cli.py `BUILTIN_SHAPES` -> `BUILTIN_MASK_SHAPES_OBJECTS`
    - shapes.py `MASK_SHAPES` -> `BUILTIN_MASK_SHAPES`
- Cleaned up calculation of built-in shape objects
- Cleaned up imports for 'test/__init__.py'
- README and wiki mention puzzle masking.

### Removed

- `make_header()` function no longer needed as header is created with f-strings now

## [3.2.0] - 2023-03-06

### Changed

- Moved build system from setup.cfg to pyproject.toml
- Added [ruff](https://github.com/charliermarsh/ruff) to the dev tool set (plus tox, pre-commit)
    - Fixed all ruff suggestions
- Moved flake8 settings to .flake8 file since pyproject.toml isn't supported
- Changed 'mode' on CSV and JSON open context managers to 'x' and let that handle any exceptions

### Removed

- `export.validate_path()`

## [3.1.0] - 2023-01-20

### Added

- `PuzzleNotGenerated` is raised if a mask is applied to a puzzle that had yet to be generated, either because it doesn't yet have words or doesn't yet have a size.
- `PuzzleSizeError` is now raised if the current puzzle size is smaller than the shortest words in the wordlist.
- Additional tests to keep coverage at 100%.

### Changed

- `WordSearch.random_words()` now accepts an "action" argument. This determines whether the random words are added ("ADD") to the current wordlist or replace ("REPLACE") the current wordlist. Defaults to "REPLACE".
- `no_duped_words()` refactored to speed up puzzle generation especially on large puzzles and puzzles with large wordlists.
- `fill_words()` refactored to stop adding words or secret words if placed words > `config.max_puzzle_words`.
- `try_to_fit_word()` refactored to no longer use deepcopy. While trying a new word, all changes are made to the actual puzzle, changes are also tracked in `previous_chars`. If a word ends up not fitting, the function backtracks and reset the puzzle to the `previous_chars`.
- `calc_puzzle_size()` now maxes out at `config.max_puzzle_words` no matter the caculation result.
- Generation tests updated to work with above changes.

### Removed

- `no_matching_neighbors()`
- `capture_all_paths_from_position()`

## [3.0.0] - 2023-01-02

### Added

- Puzzle Masking
    - Puzzle output (show(), save()) crops output to the puzzle mask so no dead space
        - Key is offset by cropped bounding box
    - CLI implementation
        - -m, --mask Mask the puzzle to a particular shape (choices: circle, diamond, triangle, heart, hexagon, octagon, pentagon, star).
        - -im, --image-mask Mask the puzzle shape to a provided image (accepts: BMP, JPEG, PNG).
- Project [documentation](https://github.com/joshbduncan/word-search-generator/wiki)
- `random_words()` method to add random words to a puzzle.
- Word class now tracks all coordinates of word (using this in place of keeping a separate 'solution' puzzle)
- Testing to make sure key only shows placed words in response to bug fixed in v2.0.1

### Changed

- CSV export no longer includes the solution
- Moved all types from 'types.py' file to appropriate object files to help with type checking
- no_duped_words() function was edited to no longer accept a WordSearch object to make testing easier
- `.show()`, `.save()`, and `.json` now crop the puzzle to the masked active area (bounding box)
- `utils.get_random_words()` now returns a list instead of a string

## [2.0.1] - 2022-10-28

### Added

- All puzzle output (stdout, csv, pdf) all indicate that '*' before a word in the key mean that word is secret (not listed in the word list) (e.g. 'Puzzle Key (*= Secret Words): ...').
    - Only shows if secret words are actually present.

### Fixed

- Answer Key and .placed_... properties were showing all words and not only words placed in the puzzle.
- JSON method returns correct word list.

## [2.0.0] - 2022-10-24
### Added

- Test for csv output with solution
- Secret Words (contributed by Chris J.M. [duck57](https://github.com/duck57))
    - The WordSearch object can now accept a list of secret bonus words
        - are included in the puzzle but not listed in the word list
        - are included in the answer key and tagged with an `*` like '\*word'.
        - A puzzle can consist of only secret words
        - Implemented in the CLI as -x, --secret-words
    - Introduced the Direction class
        - Allows for specifying either a preset numeric level or accepted cardinal direction for puzzle words.
        - Implemented in the CLI as -d, --difficulty
    - Testing for all new secret word features and accompanying functionality
    - Updated README with new features
- New `-rx, --random-secret-words` CLI argument


### Changed

- Most all supplemental function now work the base WordSearch object, reducing the of arguments needing to be passed around, and also reducing memory usage
- Puzzle config settings
    - min_puzzle_size == 5
    - max_puzzle_size == 50
    - max_puzzle_words == 100
- PDF generator updated to work with larger puzzles and word lists
- Removed the tty input from the cli as it's confusing for most users.
- CLI flag -l, --level was combined with -d, --difficulty (for backward compatibility)
- Lots of types refactoring by contributed by [duck57](https://github.com/duck57)
- clean up __main__ call to cli
- Word class
    - `WordSearch.words` property is now a set of `Word` objects
        - Allows unused words to be kept around in case they fit in re-generated version o the puzzle.
    - Allows easier tracking of all words properties
    - Allows easier access to words of different types
        - `WordSearch.words` == all available puzzle words
        - `WordSearch.placed_words` == all words placed in the puzzle (no matter of word type)
        - `WordSearch.hidden_words` == all available "regular" words
        - `WordSearch.placed_hidden_words` == all "regular" words placed in the puzzle
        - `WordSearch.secret_words` == all available "secret" words
        - `WordSearch.placed_secret_words` == all "secret" words placed in the puzzle


### Fixed

- [CLI with empty stdin causes error](https://github.com/joshbduncan/word-search-generator/issues/19)
- Corrected key coordinates to 1-based.

## [1.4.0] - 2022-09-09

### Added

- You can now export the puzzle solution along with the puzzle using the `save()` method. Just specify `solution=True` after the path.
    - If you are exporting a PDF then a second page will be added with the puzzle words highlighted in red (just like the `show(solution=True)` method)
    - If you are exporting to CSV the puzzle solution will be included at the bottom of the csv below the answer key.

### Changed

- `save()` method now accepts the `solution` argument.
- -c, --cheat cli option now works with the -o, --output option to include the puzzle solution within the output file (csv or pdf)
- To clean things up a bit, `export_pdf_file()` and `export_csv_file()` now accept a WordSearch object as the main argument.

## [1.3.0] - 2022-08-01

### Added

- -c, --cheat options for cli to show puzzle solution
- --version flag added to cli
- __eq__ magic method for checking if puzzles are the same (mostly for testing __repr__)

### Changed

- Export csv no uses the builtin csv module
- Removed colorama, now using ascii escape codes for solution highlighting
    - Updated requirements.txt and setup.cfg
- Updated __repr__ to include `level` and `size`
- Rewrote the word fitting function to use a @retry wrapper
    - Hat tip to Bob Belderbos, Twitter @bbelderbos (https://twitter.com/bbelderbos/status/1532347393009668098?s=20&t=1IOt6a8RGEohzkNKpTBrxg)
- Fixed max_puzzle_size spec in README. Was incorrectly listed as 30 when it is actually 25. Hat tip to [dt215git](https://github.com/dt215git) for the [heads-up](https://github.com/joshbduncan/word-search-generator/issues/12)

## [1.2.1] - 2022-04-01

### Added

- New generator code to make sure no duplicated exists in the puzzle
    - Generator checks during word insertion and random character fill-in stages
- JSON output property for @robguttman solver https://github.com/robguttman/word-search-solver
- Testing for new generator and export functions

### Changed

- Any input words that are palindromes are removed
- add_words() method now checks old and new words together to make sure no single word is a subset of another word

## [1.1.2] - 2022-03-14

### Changed

- Removed extra newline from output.

## [1.1.1] - 2022-03-14

### Added

- `WordSearch.show()` method
    - Allows you to show the puzzle (just like print(WordSearch)=> __str__).
    - Enables a better "solution" view using colorama "dim" with `WordSearch.show(solution=True)`.
- Required install of [colorama](https://pypi.org/project/colorama/).

### Changed

- Cleaned up some functions to work better with the new `.show()` method.

### Removed

- `WordSearch.show_solution()` method was replaced by the `WordSearch.show(solution=True)`.

## [1.1.0] - 2022-03-04

### Added

- New/cleaned-up testing.
- More type hints.

### Changed

- Tests were cleaned up and changed a bunch to pass on windows.
- Updated minimum version and testing version to Python 3.10.
- WordSearch.save() method now determines CSV or PDF export type from file name. Default to PDF is no extension if provided.
- Cleaned up variable names to match across entire project.
- Cleaned up type hints.
- Remove custom FilePath type and replace with `Union[str, Path]`.

### Removed

- Format argument on WordSearch.save() method. The file type is now determined by the provided save path. If no extension is provided it defaults to pdf.
    - Makes the -e, --export cli option no longer needed.

## [1.0.9] - 2022-02-01

### Added

- __app_name__ to init.py
- Lots of new tests to get closer to 100% coverage
- conftest.py for pytest
    - Added temp_dir fixture for testing
- setup and configure tox for testing on github

### Changed

- Added typing to correct exit status on cli
- __main__.py now passes __app_name__ to cli so help title display correctly
- Changed __str__ to print entire puzzle along with answer key
- Updated README.md with all additions, changes, fixes, and removals
- Reworked `cleanup_input()` function

### Fixed

- Puzzle solution wasn't showing correctly

### Removed

- Removed `show()` function, now just use print(object)
- Removed -k --key and -t --tabs from cli options

## [1.0.8] - 2022-01-28

### Changed

- Updated typing to simpler format
- Cleaned up all imports using isort
- Added black and isort settings to pyproject.toml
- Added optional [tests] and [dev] requirements to setup.cfg `pip install word-search-generator[dev]`
- Added isort to run file linting
- Added typing to run file


## [1.0.7] - 2021-09-22

### Added

- You can now generate puzzle from random dictionary words. No need to even supply your own words.
```bash
# just provide the -r or --random flag and the number of words you want
$ words-search -r 10
```

## [1.0.6] - 2021-09-20

### Added

- Add error check for cli when no words are provided

### Changed

- Updated PDF layout and font sizes

## [1.0.5] - 2021-09-18

### Changed

- Fully typed with mypy (for real this time)
- Corrected License type
- Updated docstrings

## [1.0.4] - 2021-09-15

### Added

- Fully typed

### Changed

- Changed all functions that took `row` and `col` to now take a tuple of (row, col) as `position`
- moved cli to cli module and out of __main__.py
- switched from setup.py to setup.cfg

## [1.0.3] - 2021-08-19

### Changed
- Changed all vars `dir` to either `direction` or `d`
- Changed puzzle size calculation and min and max value errors
- Changed pdf font size calculation to min and max boards
- Updated cli to reflect changes
- Updated PDF export
    - Now uses config variables for base font sizes
    - Grid size, grid margin, and font sizes all based on puzzle size and puzzle words
    - Implemented testing of all options to make sure all PDFs are 1-page (see also `tools/check_pdf_export_sizes.py`)
    - Installed PyPDF2 to check page count on test exports
- Swapped out some comprehensions to limit line length

## [1.0.2] - 2021-08-17

### Added

- Added some cli testing

### Changed

- Updated cli -p, --path flag to more standard -o, --output flag
- Updated cli to accept stdin of words instead of requiring -w or --words flag

```bash
# instead of using -w just list word as arguments
$ words-search some sample words to include
# all other flags work the same
$ words-search some sample words to include -l 3 -o pdf
# you can also pipe directly to word-search
$ cat some-sample-words.txt | word-search
# pipe a bunch of files for export
$ for f in tests/word*.txt; do word-search "$(cat $f)" -e pdf -o $f.pdf; done
```

## [1.0.1] - 2021-08-16

### Added

- Added testing

### Changed

- `.save()` now defaults to current directory if not specified
- Changed puzzle font multiplier calculation
- Changed `.key` to 0-based index. For display `.show()` and `.save()` still output key in 1-based index.

### Fixed

- Refactored functions
- Updated README with real life example

```python
# ---- from this ----
# if export flag make sure output path was specified
if args.export and args.path is None:
    # parser.error("-e, --export requires -p, --path.")

# ---- to this ----
# if export flag and no path flag use current directory
    if args.export and args.path is None:
        args.path = pathlib.Path.cwd()
```

## [1.0.0] - 2021-08-13

- First official release!
