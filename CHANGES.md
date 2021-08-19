# Word Search Change Log

**1.0.0** (2021-08-13)

-   First official release!

**1.0.1** (2021-08-16)

-   Refactoring functions
-   `.save()` now defaults to current directory if not specified
-   Updated README with real life example
-   Changed puzzle font multiplier calculation
-   Changed `.key` to 0-based index. For display `.show()` and `.save()` still output key in 1-based index.
-   Added testing

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

**1.0.2** (2021-08-17)

-   Added some cli testing
-   Updated cli -p, --path flag to more standard -o, --output flag
-   Updated cli to accept stdin of words instead of requiring -w or --words flag

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

**1.0.3** (2021-08-19)

-   Changed all vars `dir` to either `direction` or `d`
-   Changed puzzle size calculation and min and max value errors
-   Changed pdf font size calculation to min and max boards
-   Updated cli to reflect changes
-   Updated PDF export
    -   Now uses config variables for base font sizes
    -   Grid size, grid margin, and font sizes all based on puzzle size and puzzle words
    -   Implemented testing of all options to make sure all PDFs are 1-page (see also `tools/check_pdf_export_sizes.py`)
    -   Installed PyPDF2 to check page count on test exports
-   Swapped out some comprehensions to limit line length
