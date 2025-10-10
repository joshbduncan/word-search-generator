# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- themed word lists (issue #63), lists can be found in `src/word_search_generator/data/`
    - accessible in the base package at `WORD_LISTS` which is a `dict[str, list[str]]`
- detailed class and method documentation
- add `ty` type checker to the project (using along with mypy for now)
- cli
    - -pm/--preview-masks now also accepts an additional argument for which mask to preview (all masks are still shown if no argument is provided)
    - -pt/--preview-themes to see contents of all available themed word lists, provide a specific list as a second argument to narrow the preview
    - --examples gives argument examples to help with getting started (also included with help)

### Changed

- dropped support for python 3.10
- lots and lots of refactoring
- mask module refactor
    - improved validation
    - `method` changed from standard int to enum `MaskMethod | MethodLiteral`
    - `Mask` and `CompoundMask` classes moved into `mask.py`
- `utils.get_random_words()`
    - now returns a string of words (comma separated)
    - accepts new argument `word_list` from which to sample from (themed word lists)
- BUILTIN_MASK_SHAPES now return a dict of available mask shapes `dict[str, type[Mask]]`
- `mask.BitmapImage` changed to `mask.ImageMask`
- `Formatter.save()` method on the abstract base class now expects a value from the `ExportFormat` enum for the `format` variable
- Python 3.14 compatibility
    - updated [pyproject.toml](/pyproject.toml)
    - updated [noxfile.py](/noxfile.py)
    - updated [text.yml](/.github/workflows/test.yml)

### Fixed

- mask shape calculation (especially for small puzzle sizes)
- better error handling with more specific error messages
- enhanced type hints for better type safety

## [4.1.0] 2025-08-08

### Added

- Output word list and answer key can now be output in the original order (no sorted alphabetically) [PR #86](https://github.com/joshbduncan/word-search-generator/pull/86). Thanks [Alex Schmelkin (apumapho)](https://github.com/apumapho).
    - via the cli as `--no-sort-words`
    - via the API `WordSearch().show(sort_word_list=False)`
    - required adding [ordered-set](https://pypi.org/project/ordered-set/) to project dependencies

### Changed

- Update Word cli rich styling for better contrast between text color and background

### Fixed

- Output test now accounts for Rich styling
- Removed unused code

## [4.0.0] 2025-05-21

### Added

- OOP and ABC all the way down
    - Most key parts of this package have been extracted out into separate units allowing for more extensibility.
    - All games now derive from a base `Game` object. Each `Game` can have custom a `Generator` for generating the puzzle, a `Formatter` for displaying/outputting the puzzle, and custom word `Validator`s (e.g. no palindromes, no punctuation, no single letter words, no subwords) for validating puzzle words.
- Validators: Previously, all word validation was done during the `WordSearch` object initialization (and also after making any changes to the puzzle words). Now, the default validation (no single letter words, no palindromes, no words that fit inside of other words or encase other words) has been abstracted away. Each validator is now based on a `Validator()` abstract base class, allowing users to create their own or disable the defaults. This thought has come up before but because of issue #45 I decided to tackle. Normally in a standard word search puzzle you don't want single-letter words, calindromes, or words that are part of other words, as each of these situations could potentially lead to multiple solutions for the same puzzle.
    - `validators` argument added to `WordSearch` object
    - `--no-validators` added to cli arguments to disable default validators
    - Tests updated and added for new functionality
- `require_all_words` has been added to `Game.init()`. When set to `True` a `MissingWordError` will be raised if all provided "hidden" words can't be placed successfully. This does not take into account "secret" words. Also added to CLI as `-rall, --require-all-words`.
- `lowercase` argument added to `show` and `save` methods which outputs all puzzle letters in lowercase (as opposed to the UPPERCASE default). Added `-lc, --lowercase` flag to CLI as well. Issue #58
- all words get assigned a random color on initialization (for solution)
- custom iPython profile
    - to use first make a custom profile `ipython --profile word-search-generator`
    - then copy the include config file to your new profile `cp ipython_config.py ~/.ipython/profile_word-search-generator`
    - finally load iPython with the custom profile `ipython --profile word-search-generator`
- added pretty printed traceback via Rich
- custom alphabet can now be specified for generators (used for puzzle filler characters)
- added `-hk`, `--hide-key` to cli and `WordSearch.show()`, and `WordSearch.save()` methods, allowing user to hide the answer key during output
    - only applies to cli output and saved PDF files
    - the answer key will always be output on the solution page of a pdf

### Fixed

- Bug creating false negatives in `WordSearchGenerator.no_duped_words()` method that is used when placing new words and filler characters
- Empty puzzle shown with the `show` method was called on a puzzle that has not been generated yet, or a puzzle with no placed/valid words.

### Changed

- Minimum Python version updated to 3.10
    - Updating all typing to use the new format (instead of importing from typing)
- Tox config
- `max_fit_tries` raised to 1000 to help more words fitting within smaller puzzles
- `get_random_words()` now accepts a `max_length` argument, helpful when working with puzzles of a smaller size
- Dependencies updated and tested on latest release
    - Updated word search puzzle export to work with fpdf2 v2.7.5 changes
- None now allowed as `Game` or `Generator` validator.
- PDF output now highlights puzzle words in color "bubbles" (Issue #54)
- Updated PDF layout and formatting to better work with the new solution highlighting
- "secret" words are now highlighted and included in the word list on the solution page
- add [Rich](https://github.com/Textualize/rich) to dependencies for cli highlighting
- CLI output now defaults to a 'pretty' version using rich (can be disabled with the `--no-pretty` flag)
    - solution flag now highlights puzzle words using same coloring as PDF output
    - answer key text reversed to obfuscate (like PDF output) when not using '-c' flag
- `hide_fillers` argument added to the base `WordSearch.show()` method.

### Removed

- `reset_size()` function no longer needed as it is included inside of `_generate()` now
- removed `__version__` from init. Version info is loaded from [pyproject.toml](pyproject.toml) using `importlib.metadata.version`


## [3.5.3] 2024-12-16

### Fixes

- Output file name error on windows (fixes #80)


## [3.5.2] 2024-10-21

### Fixes

- Updated Pillow to v11.0.0 since it was breaking during install on Python 3.13

## [3.5.1] 2024-05-15

### Fixed

- Requirements

## [3.5.0] 2023-07-07

### Added

- `save()` method now also supports the `solution` argument for "CSV" and "JSON" formats. This will remove all filler characters from the saved output, leaving only characters from the placed puzzle words. Closes issues #41 and #44.
- Testing for solution highlighting in PDF output
- `cropped_size` property which gives the size (in characters) of a cropped/masked puzzle as a (width, height) tuple

### Changed

- Updated testing to use fixtures
- Standardized testing variable names

## [3.4.1]

### Fixed

- Solution highlighting on exported PDFs

## [3.4.0]

### Fixed

- `Word.offset_coordinates()`
- Secret words correctly obey their directional constraints (by duck57). Fixes issue #42.

### Changed

- `show()` method now accepts the `hide_fillers` boolean argument
    - `True` will hide all filler characters showing only the placed words (negates `solution=True`)

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
