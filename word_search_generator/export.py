import pathlib

from datetime import datetime
from fpdf import FPDF
from . import config
from . import utils


def validate_path(path: str, ftype: str) -> pathlib.Path:
    """Validate the supplied save path.

    Args:
        path (str): Path to save location.
        ftype (str): Reqeusted export file type.

    Raises:
        FileExistsError: The output path already exists as a file.
        FileNotFoundError: Output path is invalid.

    Returns:
        pathlib.Path: Validated output path for writing to.
    """
    path = pathlib.Path(path).expanduser()
    # don't overwrite any file
    if path.is_file():
        raise FileExistsError(f"Sorry, output file '{path}' already exists.")
    # check to see if outpath is a directory or a file
    if path.is_dir():
        tstamp = datetime.now().replace(microsecond=0).isoformat().replace(":", "")
        fname = "Word Search " + tstamp + ftype
        fpath = path.joinpath(fname)
    elif path.parent.exists() and path.suffix:
        fpath = path
    else:
        raise FileNotFoundError(f"Sorry, output path '{path}' is invalid.")
    # return the validated output path
    return fpath


def write_csv_file(
    fpath: pathlib.Path, puzzle: list, key: dict, level: int
) -> pathlib.Path:
    """Generate a CSV file from the current puzzle and write it to `path`.

    Args:
        fpath (pathlib.Path): Path to write the PDF to.
        puzzle (list): Completed Word Search puzzle.
        key (dict): Puzzle Answer Key.
        level (int): Puzzle level setting.

    Raises:
        OSError: The file could not be written.

    Returns:
        pathlib.Path: Final save location of the CSV file.
    """
    try:
        with open(fpath, "w") as f:
            print("** WORD SEARCH **\n", file=f)
            for row in puzzle:
                print(",".join(row), file=f)
            print(f'\n"Find these words: {utils.get_word_list_str(key)}"', file=f)
            print(f'"* Words can go {utils.get_level_dirs_str(level)}."', file=f)
            print(f'\n"Answer Key: {utils.get_answer_key_str(key)}"', file=f)
    except OSError:
        raise OSError(f"File could not be saved to '{fpath}'.")
    # return the file output path
    return fpath.absolute()


def write_pdf_file(
    fpath: pathlib.Path, puzzle: list, key: dict, level: int
) -> pathlib.Path:
    """Generate a PDF file from the current puzzle and write it to `path`.

    Args:
        fpath (pathlib.Path): Path to write the PDF to.
        puzzle (list): Completed Word Search puzzle.
        key (dict): Puzzle Answer Key.
        level (int): Puzzle level setting.

    Raises:
        OSError: The file could not be written.

    Returns:
        pathlib.Path: Final save location of the PDF file.
    """
    # setup the PDF document
    pdf = FPDF(orientation="P", unit="in", format="Letter")
    pdf.set_author(config.pdf_author)
    pdf.set_creator(config.pdf_creator)
    pdf.set_title(config.pdf_title)
    pdf.add_page()

    # draw a page border
    pdf.set_margin(0.5)
    pdf.rect(0.5, 0.5, pdf.epw, pdf.eph)
    pdf.rect(0.5, 0.5, pdf.epw, 0.5, "FD")
    # draw title box and text
    pdf.set_text_color(255)
    pdf.set_font("Courier", "B", 30)
    pdf.cell(pdf.epw, 0.5, "** WORD SEARCH **", border=0, ln=1, align="C", center=True)
    # move down and reset text fill color for puzzle
    pdf.ln(0.50)
    pdf.set_text_color(0)
    # calculate the text size based on puzzle size
    font_size = 15
    if len(puzzle) <= 15:
        font_adjust = 12 / len(puzzle)
    elif len(puzzle) <= 20:
        font_adjust = 15 / len(puzzle)
    else:
        font_adjust = 18 / len(puzzle)
    # setup grid and font sizing for puzzle characters
    pdf.set_font("Courier", size=font_size * font_adjust)
    gsize = pdf.font_size * 1.75
    # calculate new margin to make puzzle centered
    pdf.set_left_margin(pdf.epw / 2 - len(puzzle[0]) * gsize / 2 + pdf.l_margin)
    # draw the puzzle
    for row in puzzle:
        for char in row:
            pdf.multi_cell(gsize, gsize, char, align="C", ln=3)
        pdf.ln(gsize)
    # set margin, placement, and font for word list
    pdf.set_margin(1)
    pdf.ln(0.25)
    # write word list heading
    pdf.set_font("Courier", "BU", size=font_size * font_adjust)
    pdf.cell(pdf.epw, txt=f"Find these words:", border=0, align="C", ln=2)
    pdf.ln(0.125)
    pdf.set_font("Courier", size=font_size * font_adjust)
    # write the word list
    pdf.multi_cell(
        pdf.epw, pdf.font_size * 1.5, utils.get_word_list_str(key), align="C", ln=2
    )
    # move down and insert word direction info
    pdf.ln(0.125)
    pdf.set_font("Courier", size=(font_size - 3) * font_adjust)
    pdf.cell(
        w=pdf.epw,
        txt=f"* Words can go {utils.get_level_dirs_str(level)}.",
        border=0,
        align="C",
    )
    # resetting the margin before rotating makes layout easier to figure
    pdf.set_margin(0)
    # rotate the page to write answer key upside down
    with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
        pdf.set_xy(pdf.epw - pdf.epw, 0)
        pdf.set_margin(0.625)
        pdf.set_font("Courier", size=6)
        pdf.write(txt="Answer Key: " + utils.get_answer_key_str(key))
    # write the final PDF to the filesystem
    try:
        pdf.output(fpath)
    except OSError:
        raise OSError(f"File could not be saved to '{fpath}'.")
    # return the file output path
    return fpath.absolute()
