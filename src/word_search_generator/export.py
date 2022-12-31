from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF

from . import config, utils

if TYPE_CHECKING:  # pragma: no cover
    from . import WordSearch


def validate_path(path: str | Path) -> Path:
    """Validate the save path.

    Args:
        path (Union[str, Path]): Path to save location.

    Raises:
        FileExistsError: The output path already exists as a file.

    Returns:
        Path: Validated path.
    """
    # if string provided convert to pathlib Path object
    if isinstance(path, str):
        path = Path(path)
    if path.exists():
        raise FileExistsError(f"Sorry, output file '{path}' already exists.")
    return path


def write_csv_file(path: Path, ws: WordSearch) -> Path:
    """Write current puzzle to CSV format at `path`.

    Args:
        path (Path): Path to write the file to.
        ws (WordSearch): Current Word Search puzzle.

    Returns:
        Path: Final save path.
    """
    word_list = utils.get_word_list_list(ws.key)
    with open(path, mode="w") as f:
        f_writer = csv.writer(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        f_writer.writerow(["WORD SEARCH"])
        for row in ws.cropped_puzzle:
            f_writer.writerow(row)
        f_writer.writerow([""])
        f_writer.writerow(["Word List:"])
        f_writer.writerow(
            word_list
            if word_list
            else [
                "<ALL SECRET WORDS>",
            ]
        )
        f_writer.writerow(
            [f"* Words can go {utils.get_level_dirs_str(ws.directions)}."]
        )
        f_writer.writerow([""])
        answer_key_intro = (
            "Answer Key (*Secret Words)" if ws.placed_secret_words else "Answer Key"
        )
        f_writer.writerow([f"{answer_key_intro}: "])
        f_writer.writerow(utils.get_answer_key_list(ws.placed_words, ws.bounding_box))
    return path.absolute()


def write_json_file(path: Path, ws: WordSearch) -> Path:
    """Write current puzzle to JSON format at `path`.

    Args:
        path (Path): Path to write the file to.
        ws (WordSearch): Current Word Search puzzle.

    Returns:
        Path: Final save path.
    """
    with open(path, mode="w") as f:
        f.write(ws.json)
    return path.absolute()


def write_pdf_file(path: Path, puzzle: WordSearch, solution: bool = False) -> Path:
    """Write current puzzle to PDF format at `path`.

    Args:
        path (Path): Path to write the file to.
        puzzle (Type[WordSearch]): Current Word Search puzzle.
        solution (bool, optional): Include the puzzle solution. Defaults to False.

    Raises:
        OSError: File could not be written.

    Returns:
        Path: Final save path.s
    """

    # setup the PDF document
    pdf = FPDF(orientation="P", unit="in", format="Letter")
    pdf.set_author(config.pdf_author)
    pdf.set_creator(config.pdf_creator)
    pdf.set_title(config.pdf_title)
    pdf.set_line_width(pdf.line_width * 2)

    # draw initial puzzle page
    pdf = draw_puzzle_page(pdf, puzzle, False)

    # add puzzle solution page if requested
    if solution:
        pdf = draw_puzzle_page(pdf, puzzle, True)

    # write the final PDF to the filesystem
    try:
        pdf.output(path)
    except OSError:
        raise OSError(f"File could not be saved to '{path}'.")
    return path.absolute()


def draw_puzzle_page(pdf: FPDF, ws: WordSearch, solution: bool = False) -> FPDF:
    """Draw the puzzle information on a FPDF PDF page.

    Args:
        pdf (FPDF): FPDF PDF document.
        ws (WordSearch): Current Word Search puzzle.
        solution (bool, optional): Highlight the puzzle solution. Defaults to False.

    Returns:
        FPDF: FPDF PDF with drawn puzzle page.
    """

    # add a new page and setup the margins
    pdf.add_page()
    pdf.set_margin(0.5)

    # insert the title
    title = "WORD SEARCH" if not solution else "WORD SEARCH (SOLUTION)"
    pdf.set_font("Helvetica", "B", config.pdf_font_size_XXL)
    pdf.cell(pdf.epw, 0.25, title, ln=2, align="C", center=True)
    pdf.ln(0.375)

    # calculate the puzzle size and letter font size
    pdf.set_left_margin(0.75)
    gsize = config.pdf_puzzle_width / len(ws.cropped_puzzle[0])
    gmargin = 0.6875 if gsize > 36 else 0.75
    font_size = int(72 * gsize * gmargin)
    # calculate flexible font size based on word count
    # to ensure all words and the puzzle key fit on one page
    info_font_size = config.pdf_font_size_XL - (
        len(ws.words) - config.min_puzzle_words
    ) * (6 / (config.max_puzzle_words - config.min_puzzle_words))
    pdf.set_font_size(font_size)

    # draw the puzzle
    placed_words_coordinates = {
        coord
        for coords in [
            word.offset_coordinates(ws.bounding_box) for word in ws.placed_words
        ]
        for coord in coords  # type: ignore
    }  # type: ignore
    for r, row in enumerate(ws.cropped_puzzle):
        for c, char in enumerate(row):
            # draw a border around correct letters if solution was requested
            if solution and (r, c) in placed_words_coordinates:
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(gsize, gsize, char, align="C", ln=3)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.multi_cell(gsize, gsize, char, align="C", ln=3)
        pdf.ln(gsize)
    pdf.ln(0.25)

    # write word list info
    pdf.set_font("Helvetica", "BU", size=info_font_size)
    pdf.cell(
        pdf.epw,
        txt=f"Find words going {utils.get_level_dirs_str(ws.directions)}:",
        align="C",
        ln=2,
    )
    pdf.ln(0.125)

    # write word list
    word_list = utils.get_word_list_str(ws.key)
    pdf.set_font("Helvetica", "B", size=info_font_size)
    pdf.set_font_size(info_font_size)
    pdf.multi_cell(
        pdf.epw,
        info_font_size / 72 * 1.125,
        word_list if word_list else "<ALL SECRET WORDS>",
        align="C",
        ln=2,
    )

    # write the puzzle answer key
    # resetting the margin before rotating makes layout easier to figure
    pdf.set_margin(0)
    # rotate the page to write answer key upside down
    answer_key_intro = (
        "Answer Key (*Secret Words)" if ws.placed_secret_words else "Answer Key"
    )
    with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
        pdf.set_xy(pdf.epw - pdf.epw, 0)
        pdf.set_margin(0.25)
        pdf.set_font("Helvetica", size=config.pdf_font_size_S)
        pdf.write(
            txt=f"{answer_key_intro}: "
            + utils.get_answer_key_str(ws.placed_words, ws.bounding_box)
        )

    return pdf
