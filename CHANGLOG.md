# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2021-09-20
### Added
- add error check for cli when no words are provided

### Changed
- updated PDF layout and font sizes

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

