import pathlib

from datetime import datetime
from fpdf import FPDF
from typing import Union
from . import config
from . import utils


def validate_path(path: Union[str, pathlib.Path], ftype: str) -> pathlib.Path:
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
    path = pathlib.Path(path).absolute() if path else pathlib.Path.cwd()
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
    pdf.set_font("Courier", "B", config.pdf_title_font_size)
    pdf.cell(pdf.epw, 0.5, "** WORD SEARCH **", border=0, ln=1, align="C", center=True)
    # move down and reset text fill color for puzzle
    pdf.ln(0.50)
    pdf.set_text_color(0)
    # calculate the text size based on puzzle size
    font_size = config.pdf_font_size
    font_adjust = config.pdf_font_adjust / len(puzzle)
    # setup grid and font sizing for puzzle characters
    pdf.set_font("Courier", size=font_size * font_adjust)
    gmargin = config.max_puzzle_size / len(puzzle)
    gsize = (pdf.epw - gmargin) / len(puzzle)
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
    info_font_adjust = (
        font_size * font_adjust * config.pdf_font_adjust / config.max_puzzle_words
    )
    info_font_size = (
        font_size if info_font_adjust < config.pdf_font_size else info_font_adjust
    )
    pdf.set_font("Courier", "BU", size=info_font_size)
    pdf.cell(pdf.epw, txt="Find these words:", align="C", ln=2)
    pdf.ln(0.125)
    pdf.set_font("Courier", size=info_font_size)
    # write the word list
    pdf.multi_cell(pdf.epw, None, utils.get_word_list_str(key), align="C", ln=2)
    # move down and insert word direction info
    pdf.ln(0.125)
    pdf.set_font("Courier", size=info_font_size)
    pdf.cell(
        w=pdf.epw,
        txt=f"* Words can go {utils.get_level_dirs_str(level)}.",
        align="C",
    )
    # resetting the margin before rotating makes layout easier to figure
    pdf.set_margin(0)
    # rotate the page to write answer key upside down
    with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
        pdf.set_xy(pdf.epw - pdf.epw, 0)
        pdf.set_margin(0.625)
        pdf.set_font("Courier", size=config.pdf_key_font_size)
        pdf.write(txt="Answer Key: " + utils.get_answer_key_str(key))
    # write the final PDF to the filesystem
    try:
        pdf.output(fpath)
    except OSError:
        raise OSError(f"File could not be saved to '{fpath}'.")
    return fpath.absolute()
