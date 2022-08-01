# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
