import pathlib

from fpdf import FPDF

from word_search_generator import config, utils
from word_search_generator.types import FilePath, Key, Puzzle


def validate_path(path: FilePath) -> pathlib.Path:
    """Path to save location.

    Args:
        path (str): Path to save location.

    Raises:
        FileExistsError: The output path already exists as a file.
        FileNotFoundError: Output path is invalid.

    Returns:
        pathlib.Path: Validated output path.
    """

    # if string provided convert to pathlib Path object
    if isinstance(path, str):
        path = pathlib.Path(path)
    # check to make sure file type was specified
    if not path.suffix or path.suffix.lower() not in [".csv", ".pdf"]:
        path = path.with_suffix(".pdf")
    if path.exists():
        raise FileExistsError(f"Sorry, output file '{path}' already exists.")
    return path


def write_csv_file(
    path: pathlib.Path,
    puzzle: Puzzle,
    key: Key,
    level: int,
) -> pathlib.Path:
    """Write a CSV file of the current puzzle to `path`.

    Args:
        path (pathlib.Path): Path to write the CSV to.
        puzzle (Puzzle): Current Word Search puzzle.
        key (Key): Puzzle Answer Key.
        level (int): Puzzle level.

    Raises:
        OSError: The file could not be written.

    Returns:
        pathlib.Path: Final save path.
    """

    try:
        with open(path, "w") as f:
            print("** WORD SEARCH **\n", file=f)
            for row in puzzle:
                print(",".join(row), file=f)
            print(f'\n"Find these words: {utils.get_word_list_str(key)}"', file=f)
            print(f'"* Words can go {utils.get_level_dirs_str(level)}."', file=f)
            print(f'\n"Answer Key: {utils.get_answer_key_str(key)}"', file=f)
    except OSError:
        raise OSError(f"File could not be saved to '{path}'.")
    return path.absolute()


def write_pdf_file(
    path: pathlib.Path,
    puzzle: Puzzle,
    key: Key,
    level: int,
) -> pathlib.Path:
    """Write a PDF file of the current puzzle to `path`.

    Args:
        path (pathlib.Path): Path to write the CSV to.
        puzzle (Puzzle): Current Word Search puzzle.
        key (Key): Puzzle Answer Key.
        level (int): Puzzle level.

    Raises:
        OSError: The file could not be written.

    Returns:
        pathlib.Path: Final save path.
    """

    # setup the PDF document
    pdf = FPDF(orientation="P", unit="in", format="Letter")
    pdf.set_author(config.pdf_author)
    pdf.set_creator(config.pdf_creator)
    pdf.set_title(config.pdf_title)
    pdf.add_page()
    pdf.set_margin(0.5)

    # insert the title
    pdf.set_font("Helvetica", "B", config.pdf_title_font_size)
    pdf.cell(pdf.epw, 0.25, "WORD SEARCH", ln=2, align="C", center=True)
    pdf.ln(0.375)

    # calculate the puzzle size and letter font size
    pdf.set_left_margin(0.75)
    gsize = 7 / len(puzzle)
    gmargin = 0.6875 if gsize > 36 else 0.75
    font_size = 72 * gsize * gmargin
    info_font_size = font_size if font_size < 18 else 18
    pdf.set_font_size(font_size)

    # draw the puzzle
    for row in puzzle:
        for char in row:
            pdf.multi_cell(gsize, gsize, char, align="C", ln=3)
        pdf.ln(gsize)
    pdf.ln(0.25)

    # write word list info
    pdf.set_font("Helvetica", "BU", size=info_font_size)
    pdf.cell(
        pdf.epw,
        txt=f"Find words going {utils.get_level_dirs_str(level)}:",
        align="C",
        ln=2,
    )
    pdf.ln(0.125)

    # write word list
    pdf.set_font("Helvetica", "B", size=info_font_size)
    pdf.set_font_size(info_font_size)
    pdf.multi_cell(
        pdf.epw,
        info_font_size / 72 * 1.125,
        utils.get_word_list_str(key),
        align="C",
        ln=2,
    )

    # write the puzzle answer key
    # resetting the margin before rotating makes layout easier to figure
    pdf.set_margin(0)
    # rotate the page to write answer key upside down
    with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
        pdf.set_xy(pdf.epw - pdf.epw, 0)
        pdf.set_margin(0.25)
        pdf.set_font("Helvetica", size=config.pdf_key_font_size)
        pdf.write(txt="Answer Key: " + utils.get_answer_key_str(key))

    # write the final PDF to the filesystem
    try:
        pdf.output(path)
    except OSError:
        raise OSError(f"File could not be saved to '{path}'.")
    return path.absolute()
