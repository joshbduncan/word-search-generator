"""Word-search puzzle output formatting and export.

This module provides ``WordSearchFormatter``, the default
:class:`~word_search_generator.core.formatter.Formatter` implementation for
word-search puzzles.  It renders puzzles to the console via Rich tables and
exports them to CSV, JSON, and PDF files.  A set of module-level helper
functions handles the individual PDF drawing steps (title, grid, solution
highlights, word list, answer key).
"""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF, drawing
from rich import box
from rich.style import Style
from rich.table import Table
from rich.text import Text

from ..console import console
from ..core.formatter import ExportFormat, Formatter
from ..utils import (
    get_answer_key_list,
    get_answer_key_str,
    get_level_dirs_str,
    get_word_list_list,
    get_word_list_str,
)

if TYPE_CHECKING:
    from ..core import Game, Puzzle, Word


class WordSearchFormatter(Formatter):
    """Formatter that renders word-search puzzles to the console and files.

    Console output uses a Rich ``Table`` for the grid and styled ``Text``
    objects for optional solution highlighting.  File export supports CSV,
    JSON, and PDF (via fpdf2).  PDF layout is driven by the class-level
    constants below, which control page dimensions, font sizes, and the
    puzzle-grid width in inches.

    Attributes:
        PDF_AUTHOR: PDF metadata author field.
        PDF_CREATOR: PDF metadata creator field.
        PDF_TITLE: PDF metadata title field.
        PDF_FONT_SIZE_XXL: Point size used for the page title.
        PDF_FONT_SIZE_XL: Base point size for the word-list / directions text.
            Scaled down when the word count is large so everything fits on one
            page.
        PDF_FONT_SIZE_L: Point size for medium body text.
        PDF_FONT_SIZE_M: Point size for small body text.
        PDF_FONT_SIZE_S: Point size used for the upside-down answer key.
        PDF_PUZZLE_WIDTH: Width of the puzzle grid in inches on the PDF page.
        CONSOLE: The Rich ``Console`` instance used for terminal output.
    """

    # pdf export settings
    PDF_AUTHOR = "Josh Duncan"
    PDF_CREATOR = "word-search @ joshbduncan.com"
    PDF_TITLE = "Word Search Puzzle"
    PDF_FONT_SIZE_XXL = 18
    PDF_FONT_SIZE_XL = 15
    PDF_FONT_SIZE_L = 12
    PDF_FONT_SIZE_M = 9
    PDF_FONT_SIZE_S = 5
    PDF_PUZZLE_WIDTH = 7  # inches
    CONSOLE = console

    def show(
        self,
        game: Game,
        solution: bool = False,
        hide_fillers: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        reversed_letters=False,
        sort_word_list: bool = True,
    ):
        """Render the puzzle to a Rich-styled string for console output.

        Builds a ``rich.table.Table`` from the (optionally cropped) puzzle
        grid, appends the word list and answer key, and returns the whole
        block as a captured string.

        Args:
            game: The game instance to display.
            solution: Highlight placed words with per-word colours.
                Defaults to False.
            hide_fillers: Replace non-word cells with spaces so only the
                placed words are visible.  Defaults to False.
            lowercase: Convert all letters to lower case.  Defaults to False.
            hide_key: Omit the answer key from the output.  Defaults to False.
            reversed_letters: Reverse coordinate display in the answer key.
                Defaults to False.
            sort_word_list: Sort the word list alphabetically.  When False
                words appear in insertion order.  Defaults to True.

        Returns:
            The full console-ready string (table + word list + optional key).
        """

        pcopy_chars: list[list[str]] = (
            self.hide_filler_characters(game)
            if hide_fillers
            else copy.deepcopy(game.puzzle)
        )

        pcopy: list[list[Text]] = [
            [Text(ch.lower() if lowercase else ch) for ch in row] for row in pcopy_chars
        ]
        wordlist: list[Text] = []

        assert isinstance(pcopy, list)

        _word_list: list[Word] = get_word_list_list(game.words)
        if sort_word_list:
            _word_list.sort(key=lambda w: w.text)
        for word in _word_list:
            # TODO: should "secret" words be highlighted and included in wordlist
            if word.secret:
                continue
            style: Style = word.rich_style if solution else Style()
            wordlist.append(
                Text(word.text.lower() if lowercase else word.text, style=style)
            )
            for r, c in word.coordinates:
                pcopy[r][c] = Text(
                    game.puzzle[r][c].lower() if lowercase else game.puzzle[r][c],
                    style=style,
                )

        table = Table(
            title="WORD SEARCH",
            title_style="bold italic",
            box=box.HORIZONTALS,
            padding=0,
            show_edge=True,
            show_header=False,
            show_lines=False,
        )

        min_x, min_y = game.bounding_box[0]
        max_x, max_y = game.bounding_box[1]

        for _ in range(max_x - min_x + 1):
            table.add_column(width=1, justify="center", vertical="middle", no_wrap=True)

        for row in pcopy[min_y : max_y + 1]:
            table.add_row(*row[min_x : max_x + 1])

        answer_key = "Answer Key"
        if game.placed_secret_words:  # type:ignore [attr-defined]
            answer_key += " (*Secret Words)"
        answer_key += ": "

        word_key_strings = get_answer_key_list(
            _word_list,
            game.bounding_box,
            lowercase,
            reversed_letters,
        )
        answer_key += ", ".join(key_string for key_string in word_key_strings)

        with self.CONSOLE.capture() as capture:
            self.CONSOLE.print(table)
            self.CONSOLE.print(f"Find words going {get_level_dirs_str(game.level)}:")
            self.CONSOLE.print(*wordlist, sep=", ")
            self.CONSOLE.print()
            if not hide_key:
                self.CONSOLE.print(answer_key)
        return capture.get()

    def save(
        self,
        game: Game,
        path: str | Path,
        format: ExportFormat = ExportFormat.PDF,
        solution: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        sort_word_list: bool = True,
    ) -> Path:
        """Dispatch puzzle export to the correct writer.

        Converts a bare string path to a :class:`~pathlib.Path`, then
        routes to :meth:`write_csv_file`, :meth:`write_json_file`, or
        :meth:`write_pdf_file` based on ``format``.

        Args:
            game: The game instance to save.
            path: Destination file path (string or Path).
            format: Target container format.  Defaults to ``ExportFormat.PDF``.
            solution: Include a solution page / solution-only grid.
                Defaults to False.
            lowercase: Write all letters in lower case.  Defaults to False.
            hide_key: Omit the answer key (PDF only).  Defaults to False.
            sort_word_list: Sort the word list alphabetically.  Defaults to True.

        Returns:
            The absolute path of the file that was written.
        """
        # convert strings to PATH object
        if isinstance(path, str):
            path = Path(path)

        match format:
            case ExportFormat.CSV:
                saved_file = self.write_csv_file(
                    path,
                    game,
                    solution,
                    lowercase,
                    sort_word_list,
                )
            case ExportFormat.JSON:
                saved_file = self.write_json_file(
                    path,
                    game,
                    solution,
                    lowercase,
                    sort_word_list,
                )
            case _:
                saved_file = self.write_pdf_file(
                    path, game, solution, lowercase, hide_key, sort_word_list
                )

        # return saved file path
        return saved_file

    def write_csv_file(
        self,
        path: Path,
        game: Game,
        solution: bool = False,
        lowercase: bool = False,
        sort_word_list: bool = True,
        *args,
        **kwargs,
    ) -> Path:
        """Write the puzzle to a CSV file.

        The file contains the grid rows, the word list, the allowed
        directions, and the answer key.  When ``solution`` is True filler
        characters are stripped from the grid so only placed-word letters
        remain.

        Args:
            path: Destination file path.  Must not already exist.
            game: The game instance to export.
            solution: Strip filler characters from the grid.
                Defaults to False.
            lowercase: Convert all text to lower case.  Defaults to False.
            sort_word_list: Sort the word list alphabetically.
                Defaults to True.

        Returns:
            The absolute path of the written file.

        Raises:
            FileExistsError: If ``path`` already exists on disk.
        """
        word_list = get_word_list_list(game.words)
        if sort_word_list:
            word_list.sort(key=lambda w: w.text)

        puzzle = self.hide_filler_characters(game) if solution else game.cropped_puzzle
        level_dirs_str = get_level_dirs_str(game.level)
        key_intro = "Answer Key"
        if hasattr(game, "placed_secret_words"):
            key_intro += " (*Secret Words)"
        answer_key_list = get_answer_key_list(word_list, game.bounding_box)
        word_list_as_strings = [word.text for word in word_list]

        # lower case was requested change case or letters for puzzle, words, and key
        if lowercase:
            word_list_as_strings = [word.lower() for word in word_list_as_strings]
            puzzle = [[c.lower() for c in line] for line in puzzle]
            for i, s in enumerate(answer_key_list):
                parts = s.split(" ")
                answer_key_list[i] = parts[0].lower() + " " + " ".join(parts[1:])

        # catch case of all secret words
        if not word_list_as_strings:
            word_list_as_strings = ["<ALL SECRET WORDS>"]

        with open(path, "x", newline="", encoding="utf-8") as f:
            f_writer = csv.writer(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            f_writer.writerow(["WORD SEARCH"])
            for row in puzzle:
                f_writer.writerow(row)
            f_writer.writerow([""])
            f_writer.writerow(["Word List:"])
            f_writer.writerow(word_list_as_strings)
            f_writer.writerow([f"* Words can go {level_dirs_str}."])
            f_writer.writerow([""])
            f_writer.writerow([f"{key_intro}: "])
            f_writer.writerow(answer_key_list)
        return path.absolute()

    def write_json_file(
        self,
        path: Path,
        game: Game,
        solution: bool = False,
        lowercase: bool = False,
        sort_word_list: bool = True,
        *args,
        **kwargs,
    ) -> Path:
        """Write the puzzle to a JSON file.

        The JSON object contains three keys: ``puzzle`` (the 2-D grid),
        ``words`` (the word list), and ``key`` (per-word placement info
        from :attr:`~word_search_generator.core.word.Word.key_info_json`).

        Args:
            path: Destination file path.  Must not already exist.
            game: The game instance to export.
            solution: Strip filler characters from the grid.
                Defaults to False.
            lowercase: Convert all text to lower case.  Defaults to False.
            sort_word_list: Sort the word list alphabetically.
                Defaults to True.

        Returns:
            The absolute path of the written file.

        Raises:
            FileExistsError: If ``path`` already exists on disk.
        """
        word_list = get_word_list_list(game.words)
        if sort_word_list:
            word_list.sort(key=lambda w: w.text)

        puzzle = self.hide_filler_characters(game) if solution else game.cropped_puzzle

        # lower case was requested change case or letters for puzzle, words, and key
        if lowercase:
            puzzle = [[c.lower() for c in line] for line in puzzle]

        data = json.dumps(
            {
                "puzzle": puzzle,
                "words": [
                    word.text.lower() if lowercase else word.text for word in word_list
                ],
                "key": {
                    word.text.lower() if lowercase else word.text: word.key_info_json
                    for word in word_list
                },
            }
        )
        with open(path, "x") as f:
            f.write(data)
        return path.absolute()

    def write_pdf_file(
        self,
        path: Path,
        game: Game,
        solution: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        sort_word_list: bool = True,
    ) -> Path:
        """Write the puzzle to a Letter-sized PDF file.

        Always produces a puzzle page.  When ``solution`` is True a second
        page is appended with the words highlighted in colour.  The answer
        key is printed upside-down at the bottom of the puzzle page unless
        ``hide_key`` is True.

        Args:
            path: Destination file path.  Must not already exist.
            game: The game instance to export.
            solution: Append a solution page.  Defaults to False.
            lowercase: Convert all letters to lower case.  Defaults to False.
            hide_key: Omit the upside-down answer key.  Defaults to False.
            sort_word_list: Sort the word list alphabetically.
                Defaults to True.

        Returns:
            The absolute path of the written file.

        Raises:
            FileExistsError: If ``path`` already exists on disk.
            OSError: If the file system refuses the write.
        """
        # setup the PDF document
        pdf = FPDF(orientation="P", unit="in", format="Letter")
        pdf.set_author(self.PDF_AUTHOR)
        pdf.set_creator(self.PDF_CREATOR)
        pdf.set_title(self.PDF_TITLE)
        pdf.set_line_width(pdf.line_width * 2)

        # draw initial puzzle page
        draw_puzzle_page(self, pdf, game, False, lowercase, hide_key, sort_word_list)

        # add puzzle solution page if requested
        if solution:
            draw_puzzle_page(
                self, pdf, game, True, lowercase, sort_word_list=sort_word_list
            )

        # check the provided path since fpdf doesn't offer context manager
        if path.exists():
            raise FileExistsError(f"Sorry, output file '{path}' already exists.")

        # write the final PDF to the filesystem
        try:
            pdf.output(path)
        except OSError as e:
            e.add_note(f"File could not be saved to '{path}'.")
            raise
        return path.absolute()

    @staticmethod
    def hide_filler_characters(
        game: Game,
    ) -> Puzzle:
        """Return a copy of the puzzle with every non-word cell blanked.

        Iterates over the full grid and replaces any cell whose
        ``(col, row)`` coordinate is not part of a placed word with a
        single space.  The original ``game.puzzle`` is not mutated.

        Args:
            game: The game instance whose puzzle grid is blanked.

        Returns:
            A deep copy of the puzzle grid with filler cells set to ``" "``.
        """
        output: Puzzle = copy.deepcopy(game.puzzle)
        word_coords = {
            coord
            for coords in [word.coordinates for word in game.placed_words]
            for coord in coords
        }
        for row in range(game.size):
            for col in range(game.size):
                if (col, row) not in word_coords:
                    output[col][row] = " "
        return output


def draw_page_title(title: str, pdf: FPDF, formatter: WordSearchFormatter):
    """Write a bold, centred title at the current PDF cursor position.

    Args:
        title: Text to render (e.g. ``"WORD SEARCH"``).
        pdf: The active FPDF document.
        formatter: Formatter instance whose font-size constants are used.
    """
    pdf.set_font("Helvetica", "B", formatter.PDF_FONT_SIZE_XXL)
    pdf.cell(pdf.epw, 0.25, title, new_y="NEXT", align="C", center=True)
    pdf.ln(0.125)


def draw_puzzle(pdf: FPDF, game: Game, gsize: float, lowercase: bool = False) -> None:
    """Render the puzzle grid as a table of single-character cells.

    Each cell is a square with side length ``gsize`` inches.  The grid is
    taken from :attr:`~word_search_generator.core.game.Game.cropped_puzzle`
    so masked / inactive border rows are already stripped.

    Args:
        pdf: The active FPDF document.
        game: The game instance whose cropped puzzle is drawn.
        gsize: Cell side length in inches.
        lowercase: Convert every letter to lower case.  Defaults to False.
    """
    for row in game.cropped_puzzle:
        for char in row:
            pdf.cell(
                gsize,
                gsize,
                char.lower() if lowercase else char,
                align="C",
            )
        pdf.ln(gsize)
    pdf.ln(0.25)


def highlight_solution(
    pdf: FPDF, game: Game, gsize: float, start_x: float, start_y: float
):
    """Draw a coloured stroke through each placed word on the PDF page.

    Each word gets a semi-transparent line from its first letter centre to
    its last letter centre, using the per-word colour assigned at creation
    time.  Words whose start or end position cannot be resolved are
    silently skipped.

    Args:
        pdf: The active FPDF document.
        game: The game instance containing placed words.
        gsize: Cell side length in inches (same value used by
            :func:`draw_puzzle`).
        start_x: X coordinate (inches) of the top-left corner of the
            puzzle grid on the page.
        start_y: Y coordinate (inches) of the top-left corner of the
            puzzle grid on the page.
    """
    for word in game.placed_words:
        word_start, *_, word_end = word.offset_coordinates(game.bounding_box)
        word_start_x, word_start_y = word_start
        word_end_x, word_end_y = word_end

        # mypy check for word position
        if not word_start_x or not word_start_y or not word_end_x or not word_end_y:
            continue

        with pdf.new_path() as path:
            path.style.fill_color = None
            path.style.stroke_color = drawing.DeviceRGB(*word.color, 0.5)
            path.style.stroke_join_style = "round"
            path.style.stroke_width = pdf.font_size * 0.875
            path.move_to(
                start_x + ((word_start_x - 1) * gsize) + (gsize / 2),
                start_y + ((word_start_y - 1) * gsize) + (gsize / 2),
            )
            path.line_to(
                start_x + ((word_end_x - 1) * gsize) + (gsize / 2),
                start_y + ((word_end_y - 1) * gsize) + (gsize / 2),
            )


def draw_word_list(
    pdf: FPDF,
    game: Game,
    info_font_size: float,
    solution: bool = False,
    lowercase: bool = False,
    sort_word_list: bool = True,
):
    """Render the directions hint and the word list below the puzzle grid.

    Words are laid out in centred, wrapping lines that fit the effective
    page width.  On a solution page each word is additionally underlined
    with the same semi-transparent colour stroke used in the grid
    highlights.  Secret words are included only when ``solution`` is True;
    if the list would otherwise be empty a placeholder label is printed.

    Args:
        pdf: The active FPDF document.
        game: The game instance whose words are listed.
        info_font_size: Point size for the word-list text (already scaled
            by the caller based on word count).
        solution: Include secret words and draw colour underlines.
            Defaults to False.
        lowercase: Convert all word text to lower case.  Defaults to False.
        sort_word_list: Sort the word list alphabetically.  Defaults to True.
    """
    level_dirs_str = get_level_dirs_str(game.level)
    pdf.set_font("Helvetica", "BU", size=info_font_size)
    pdf.cell(
        pdf.epw,
        text=f"Find words going {level_dirs_str}:",
        align="C",
        new_y="NEXT",
    )
    pdf.ln(0.125)

    # write word list
    pdf.set_font("Helvetica", "B", size=info_font_size)
    pdf.set_font_size(info_font_size)
    pdf.set_char_spacing(0.5)

    word_list = get_word_list_list(game.words)
    if sort_word_list:
        word_list.sort(key=lambda w: w.text)

    lines: list[tuple[float, list[Word]]] = []
    line_width = 0.0
    line: list[Word] = []
    for word in word_list:
        if word.secret and not solution:
            continue
        word_cell_width = pdf.get_string_width(word.text) + pdf.c_margin * 4
        if line_width + word_cell_width > pdf.epw:
            lines.append((line_width, line))
            line_width = 0.0
            line = []
        line_width += word_cell_width
        line.append(word)
    if line:
        lines.append((line_width, line))

    for line_width, words in lines:
        line_offset = (pdf.epw - line_width) / 2
        pdf.set_x(pdf.get_x() + line_offset)
        for word in words:
            if word.secret and not solution:
                continue
            start_x = pdf.get_x()
            start_y = pdf.get_y()
            word_cell_width = pdf.get_string_width(word.text) + pdf.c_margin * 4
            pdf.cell(
                w=word_cell_width,
                text=word.text.lower() if lowercase else word.text,
                align="C",
            )
            if solution:
                with pdf.new_path() as path:
                    path.style.fill_color = None
                    r, g, b = word.color
                    path.style.stroke_color = drawing.DeviceRGB(r, g, b, 0.5)
                    path.style.stroke_join_style = "round"
                    path.style.stroke_width = pdf.font_size * 0.875
                    path.move_to(
                        start_x + pdf.c_margin * 2.75,
                        start_y + (pdf.font_size / 2),
                    )
                    path.line_to(
                        pdf.get_x() - pdf.c_margin * 2.75,
                        pdf.get_y() + (pdf.font_size / 2),
                    )

        pdf.ln(pdf.font_size * 1.25)

    if not lines and not solution:
        pdf.cell(text="<ALL SECRET WORDS>", align="C", center=True)


def draw_puzzle_key(
    formatter: WordSearchFormatter,
    pdf: FPDF,
    game: Game,
    lowercase: bool = False,
    sort_word_list: bool = True,
):
    """Print the answer key upside-down at the bottom of the current page.

    The page is rotated 180 degrees around its centre, the text cursor is
    moved to what is visually the bottom margin, and the key is written in
    the smallest font size.  This means the reader must flip the page to
    read it without accidentally glancing at the answers.

    Args:
        formatter: Formatter instance whose ``PDF_FONT_SIZE_S`` constant is
            used for the key text.
        pdf: The active FPDF document.
        game: The game instance whose answer key is rendered.
        lowercase: Convert word names in the key to lower case.
            Defaults to False.
        sort_word_list: Sort the word list alphabetically.  Defaults to True.
    """
    word_list = get_word_list_list(game.words)
    if sort_word_list:
        word_list.sort(key=lambda w: w.text)

    key_intro = "Answer Key"
    if hasattr(game, "placed_secret_words"):
        key_intro += " (*Secret Words)"
    answer_key_str = get_answer_key_str(word_list, game.bounding_box)

    # if lower case requested, change for letters for puzzle, words, and key
    if lowercase:
        for word in word_list:
            answer_key_str = answer_key_str.replace(word.text, word.text.lower())

    # write the puzzle answer key
    # resetting the margin before rotating makes layout easier to figure
    pdf.set_margin(0)
    pdf.set_char_spacing(0)
    # rotate the page to write answer key upside down
    with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
        pdf.set_xy(pdf.epw - pdf.epw, 0)
        pdf.set_margin(0.25)
        pdf.set_font("Helvetica", size=formatter.PDF_FONT_SIZE_S)
        pdf.write(text=f"{key_intro}: {answer_key_str}")


def draw_puzzle_page(
    formatter: WordSearchFormatter,
    pdf: FPDF,
    game: Game,
    solution: bool = False,
    lowercase: bool = False,
    hide_key: bool = False,
    sort_word_list: bool = True,
) -> None:
    """Compose a full puzzle page inside an FPDF document.

    Adds a new page, writes the title, draws the grid, optionally overlays
    solution highlights, prints the word list, and (unless suppressed)
    renders the upside-down answer key.  Font sizes are scaled so that
    puzzles with many words still fit on a single Letter-sized page.

    Args:
        formatter: Formatter instance whose PDF constants drive layout.
        pdf: The active FPDF document; a new page is appended.
        game: The game instance to render.
        solution: Overlay coloured word highlights and include secret words
            in the word list.  Defaults to False.
        lowercase: Convert all letters to lower case.  Defaults to False.
        hide_key: Omit the upside-down answer key.  Defaults to False.
        sort_word_list: Sort the word list alphabetically.  Defaults to True.
    """

    # add a new page and setup the margins
    pdf.add_page()
    pdf.set_margin(0.5)

    # insert the title
    draw_page_title(
        "WORD SEARCH" if not solution else "WORD SEARCH (SOLUTION)", pdf, formatter
    )

    # calculate the puzzle size and letter font size
    pdf.set_left_margin(0.75)
    gsize = formatter.PDF_PUZZLE_WIDTH / game.cropped_size[0]
    gmargin = 0.6875 if gsize > 36 else 0.75
    font_size = int(72 * gsize * gmargin)
    # calculate flexible font size based on word count
    # to ensure all words and the puzzle key fit on one page
    info_font_size = formatter.PDF_FONT_SIZE_XL - (
        len(game.words) - game.MIN_PUZZLE_WORDS
    ) * (6 / (game.MAX_PUZZLE_WORDS - game.MIN_PUZZLE_WORDS))
    pdf.set_font_size(font_size)

    # get start position of puzzle
    start_x = pdf.get_x()
    start_y = pdf.get_y()

    # draw the puzzle
    draw_puzzle(pdf, game, gsize, lowercase)

    # draw solution highlights
    if solution:
        highlight_solution(pdf, game, gsize, start_x, start_y)

    # collect puzzle information
    word_list_str = get_word_list_str(game.words)

    # catch case of all secret words
    if not word_list_str:
        word_list_str = "<ALL SECRET WORDS>"

    draw_word_list(pdf, game, info_font_size, solution, lowercase, sort_word_list)

    if not hide_key:
        draw_puzzle_key(formatter, pdf, game, lowercase, sort_word_list)
