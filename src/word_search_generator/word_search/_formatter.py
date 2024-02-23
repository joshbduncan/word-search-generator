from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fpdf import FPDF, drawing
from rich import box
from rich.style import Style
from rich.table import Table
from rich.text import Text

from .. import utils
from ..console import console
from ..core.formatter import Formatter
from ..core.game import Game

if TYPE_CHECKING:  # pragma: no cover
    from ..core.game import Puzzle
    from ..core.word import Word
    from .word_search import WordSearch


class WordSearchFormatter(Formatter):
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

    def show(
        self,
        game: Game,
        solution: bool = False,
        hide_fillers: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ):
        """Return a string representation of the game.

        Args:
            solution: Highlight the puzzle solution. Defaults to False.
            hide_fillers: Hide filler letters (show only words). Defaults to False.
            lowercase: Change letters to lower case. Defaults to False.
        """
        pcopy: list[list[Any]] = copy.deepcopy(game.puzzle)
        wordlist = []

        sorted_words = sorted(game.placed_words, key=lambda w: w.text)
        for word in sorted_words:
            # TODO: should "secret" words be highlighted and included in wordlist
            if word.secret:
                continue
            style = word.rich_style if solution else Style()
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
            if lowercase:
                row = [c.lower() if isinstance(c, str) else c for c in row]
            table.add_row(*row[min_x : max_x + 1])

        answer_key = "Answer Key"
        if game.placed_secret_words:  # type:ignore [attr-defined]
            answer_key += " (*Secret Words)"
        answer_key += ":"

        word_key_strings = utils.get_answer_key_list(
            game.placed_words, game.bounding_box, lowercase
        )
        answer_key += ", ".join(
            key_string.replace("(", "#").replace(")", "(").replace("#", ")")[::-1]
            for key_string in word_key_strings
        )

        with console.capture() as capture:
            console.print(table)
            console.print(f"Find words going {utils.get_LEVEL_DIRS_str(game.level)}:")
            console.print(*wordlist, sep=", ")
            console.print()
            console.print(answer_key)
        return capture.get()

    def save(
        self,
        game: Game,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        if format.upper() not in ["CSV", "JSON", "PDF"]:
            raise ValueError('Save file format must be either "CSV", "JSON", or "PDF".')
        # convert strings to PATH object
        if isinstance(path, str):
            path = Path(path)
        if format.upper() == "CSV":
            saved_file = self.write_csv_file(
                path,
                game,  # type: ignore
                solution,
                lowercase,
            )
        elif format.upper() == "JSON":
            saved_file = self.write_json_file(
                path,
                game,  # type: ignore
                solution,
                lowercase,
            )
        else:
            saved_file = self.write_pdf_file(
                path,
                game,  # type: ignore
                solution,
                lowercase,
            )
        # return saved file path
        return saved_file

    def write_csv_file(
        self,
        path: Path,
        game: WordSearch,
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        word_list = utils.get_word_list_list(game.key)
        puzzle = self.hide_filler_characters(game) if solution else game.cropped_puzzle
        LEVEL_DIRS_str = utils.get_LEVEL_DIRS_str(game.level)
        key_intro = "Answer Key"
        if hasattr(game, "placed_secret_words"):
            key_intro += " (*Secret Words)"
        answer_key_list = utils.get_answer_key_list(
            game.placed_words, game.bounding_box
        )

        # lower case was requested change case or letters for puzzle, words, and key
        if lowercase:
            word_list = [word.lower() for word in word_list]
            puzzle = [[c.lower() for c in line] for line in puzzle]
            for i, s in enumerate(answer_key_list):
                parts = s.split(" ")
                answer_key_list[i] = parts[0].lower() + " " + " ".join(parts[1:])

        # catch case of all secret words
        if not word_list:
            word_list = ["<ALL SECRET WORDS>"]

        with open(path, "x", newline="", encoding="utf-8") as f:
            f_writer = csv.writer(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            f_writer.writerow(["WORD SEARCH"])
            for row in puzzle:
                f_writer.writerow(row)
            f_writer.writerow([""])
            f_writer.writerow(["Word List:"])
            f_writer.writerow(word_list)
            f_writer.writerow([f"* Words can go {LEVEL_DIRS_str}."])
            f_writer.writerow([""])
            f_writer.writerow([f"{key_intro}: "])
            f_writer.writerow(answer_key_list)
        return path.absolute()

    def write_json_file(
        self,
        path: Path,
        game: WordSearch,
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        word_list = utils.get_word_list_list(game.key)
        puzzle = self.hide_filler_characters(game) if solution else game.cropped_puzzle

        # lower case was requested change case or letters for puzzle, words, and key
        if lowercase:
            word_list = [word.lower() for word in word_list]
            puzzle = [[c.lower() for c in line] for line in puzzle]

        data = json.dumps(
            {
                "puzzle": puzzle,
                "words": [
                    word.text.lower() if lowercase else word.text
                    for word in game.placed_words
                ],
                "key": {
                    word.text.lower() if lowercase else word.text: word.key_info_json
                    for word in game.placed_words
                },
            }
        )
        with open(path, "x") as f:
            f.write(data)
        return path.absolute()

    def write_pdf_file(
        self,
        path: Path,
        game: WordSearch,
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        def draw_puzzle_page(
            pdf: FPDF, game: WordSearch, solution: bool = False
        ) -> FPDF:
            """Draw the puzzle information on a FPDF PDF page.

            Args:
                pdf (FPDF): FPDF PDF document.
                game (Game): Current Word Search puzzle.
                solution (bool, optional): Highlight the puzzle solution.
                Defaults to False.

            Returns:
                FPDF: FPDF PDF with drawn puzzle page.
            """

            # add a new page and setup the margins
            pdf.add_page()
            pdf.set_margin(0.5)

            # insert the title
            title = "WORD SEARCH" if not solution else "WORD SEARCH (SOLUTION)"
            pdf.set_font("Helvetica", "B", self.PDF_FONT_SIZE_XXL)
            pdf.cell(pdf.epw, 0.25, title, new_y="NEXT", align="C", center=True)
            pdf.ln(0.125)

            # calculate the puzzle size and letter font size
            pdf.set_left_margin(0.75)
            gsize = self.PDF_PUZZLE_WIDTH / game.cropped_size[0]
            gmargin = 0.6875 if gsize > 36 else 0.75
            font_size = int(72 * gsize * gmargin)
            # calculate flexible font size based on word count
            # to ensure all words and the puzzle key fit on one page
            info_font_size = self.PDF_FONT_SIZE_XL - (
                len(game.words) - Game.MIN_PUZZLE_WORDS
            ) * (6 / (Game.MAX_PUZZLE_WORDS - Game.MIN_PUZZLE_WORDS))
            pdf.set_font_size(font_size)

            # get start position of puzzle
            start_x = pdf.get_x()
            start_y = pdf.get_y()

            # draw the puzzle
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

            # draw solution highlights
            if solution:
                for word in game.placed_words:
                    word_start, *_, word_end = word.offset_coordinates(
                        game.bounding_box
                    )
                    word_start_x, word_start_y = word_start
                    word_end_x, word_end_y = word_end

                    # mypy check for word position
                    if (
                        not word_start_x
                        or not word_start_y
                        or not word_end_x
                        or not word_end_y
                    ):
                        continue  # pragma: no cover

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

            # collect puzzle information
            word_list_str = utils.get_word_list_str(game.key)
            LEVEL_DIRS_str = utils.get_LEVEL_DIRS_str(game.level)
            key_intro = "Answer Key"
            if hasattr(game, "placed_secret_words"):
                key_intro += " (*Secret Words)"
            answer_key_str = utils.get_answer_key_str(
                game.placed_words, game.bounding_box
            )

            # if lower case requested, change for letters for puzzle, words, and key
            if lowercase:
                for word in game.placed_words:
                    answer_key_str = answer_key_str.replace(
                        word.text, word.text.lower()
                    )

            # catch case of all secret words
            if not word_list_str:
                word_list_str = "<ALL SECRET WORDS>"

            # write word list info
            pdf.set_font("Helvetica", "BU", size=info_font_size)
            pdf.cell(
                pdf.epw,
                text=f"Find words going {LEVEL_DIRS_str}:",
                align="C",
                new_y="NEXT",
            )
            pdf.ln(0.125)

            # write word list
            pdf.set_font("Helvetica", "B", size=info_font_size)
            pdf.set_font_size(info_font_size)
            pdf.set_char_spacing(0.5)

            sorted_words = sorted(game.placed_words, key=lambda w: w.text)
            lines: list[tuple[float, list[Word]]] = []
            line_width = 0.0
            line: list[Word] = []
            for word in sorted_words:
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
                    if word.secret and not solution:  # pragma: no cover
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
                            path.style.stroke_color = drawing.DeviceRGB(
                                *word.color, 0.5
                            )
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

            # write the puzzle answer key
            # resetting the margin before rotating makes layout easier to figure
            pdf.set_margin(0)
            pdf.set_char_spacing(0)
            # rotate the page to write answer key upside down
            with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
                pdf.set_xy(pdf.epw - pdf.epw, 0)
                pdf.set_margin(0.25)
                pdf.set_font("Helvetica", size=self.PDF_FONT_SIZE_S)
                pdf.write(text=f"{key_intro}: {answer_key_str}")

            return pdf

        # setup the PDF document
        pdf = FPDF(orientation="P", unit="in", format="Letter")
        pdf.set_author(self.PDF_AUTHOR)
        pdf.set_creator(self.PDF_CREATOR)
        pdf.set_title(self.PDF_TITLE)
        pdf.set_line_width(pdf.line_width * 2)

        # draw initial puzzle page
        pdf = draw_puzzle_page(pdf, game)

        # add puzzle solution page if requested
        if solution:
            pdf = draw_puzzle_page(pdf, game, solution)

        # check the provided path since fpdf doesn't offer context manager
        if path.exists():
            raise FileExistsError(f"Sorry, output file '{path}' already exists.")

        # write the final PDF to the filesystem
        try:
            pdf.output(path)
        except OSError:
            raise OSError(f"File could not be saved to '{path}'.")
        return path.absolute()

    def format_puzzle_for_show(
        self,
        game: WordSearch,
        show_solution: bool = False,
        hide_fillers: bool = False,
        lowercase: bool = False,
    ) -> str:
        word_list_str = utils.get_word_list_str(game.key)
        # prepare the correct version of the puzzle
        if hide_fillers:
            puzzle_list = self.hide_filler_characters(game)
        elif show_solution:
            puzzle_list = self.highlight_solution(game)
        else:
            puzzle_list = game.puzzle
        # calculate header length based on cropped puzzle size to account for masks
        header_width = max(
            11, (game.bounding_box[1][0] - game.bounding_box[0][0] + 1) * 2 - 1
        )
        hr = "-" * header_width
        header = hr + "\n" + f"{'WORD SEARCH':^{header_width}}" + "\n" + hr
        puzzle_str = utils.stringify(puzzle_list, game.bounding_box)
        LEVEL_DIRS_str = utils.get_LEVEL_DIRS_str(game.level)
        key_intro = "Answer Key"
        if hasattr(game, "placed_secret_words"):
            key_intro += " (*Secret Words)"
        answer_key_str = utils.get_answer_key_str(game.placed_words, game.bounding_box)

        # lower case was requested change case or letters for puzzle, words, and key
        if lowercase:
            word_list_str = word_list_str.lower()
            puzzle_str = puzzle_str.lower()
            for word in game.placed_words:
                answer_key_str = answer_key_str.replace(word.text, word.text.lower())

        # catch case of all secret words
        if not word_list_str:
            word_list_str = "<ALL SECRET WORDS>"

        output = ""
        output += f"{header}\n"
        output += f"{puzzle_str}\n\n"
        output += f"Find these words: {word_list_str}\n"
        output += f"* Words can go {LEVEL_DIRS_str}\n\n"
        output += f"{key_intro}: {answer_key_str}"
        return output

    def highlight_solution(self, game: WordSearch) -> Puzzle:
        """Add highlighting to puzzle solution."""
        output: Puzzle = copy.deepcopy(game.puzzle)
        for word in game.placed_words:
            if (
                word.start_column is None
                or word.start_row is None
                or word.direction is None
            ):  # only here for mypy
                continue  # pragma: no cover
            x = word.start_column
            y = word.start_row
            for char in word.text:
                output[y][x] = f"\u001b[1m\u001b[31m{char}\u001b[0m"
                x += word.direction.c_move
                y += word.direction.r_move
        return output

    def hide_filler_characters(
        self,
        game: WordSearch,
    ) -> Puzzle:
        """Remove filler characters from a puzzle."""
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
