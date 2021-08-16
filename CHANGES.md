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
