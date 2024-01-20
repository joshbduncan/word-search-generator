from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF

from .. import config, utils
from . import Formatter

if TYPE_CHECKING:  # pragma: no cover
    from ..game import Game, Puzzle


class WordSearchFormatter(Formatter):
    def show(
        self,
        game: Game,
        solution: bool = False,
        hide_fillers: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> str:
        """Return a string representation of the game.

        Args:
            solution: Highlight the puzzle solution. Defaults to False.
            hide_fillers: Hide filler letters (show only words). Defaults to False.
            lowercase: Change letters to lower case. Defaults to False.
        """
        return self.format_puzzle_for_show(game, solution, hide_fillers, lowercase)

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
            saved_file = self.write_csv_file(path, game, solution, lowercase)
        elif format.upper() == "JSON":
            saved_file = self.write_json_file(path, game, solution, lowercase)
        else:
            saved_file = self.write_pdf_file(path, game, solution, lowercase)
        # return saved file path
        return saved_file

    def write_csv_file(
        self,
        path: Path,
        game: Game,
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        word_list = utils.get_word_list_list(game.key)
        puzzle = self.hide_filler_characters(game) if solution else game.cropped_puzzle
        level_dirs_str = utils.get_level_dirs_str(game.level)
        key_intro = (
            "Answer Key (*Secret Words)" if game.placed_secret_words else "Answer Key"
        )
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
        game: Game,
        solution: bool = False,
        lowercase: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        def draw_puzzle_page(pdf: FPDF, game: Game, solution: bool = False) -> FPDF:
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
            pdf.set_font("Helvetica", "B", config.pdf_font_size_XXL)
            pdf.cell(pdf.epw, 0.25, title, new_y="NEXT", align="C", center=True)
            pdf.ln(0.375)

            # calculate the puzzle size and letter font size
            pdf.set_left_margin(0.75)
            gsize = config.pdf_puzzle_width / game.cropped_size[0]
            gmargin = 0.6875 if gsize > 36 else 0.75
            font_size = int(72 * gsize * gmargin)
            # calculate flexible font size based on word count
            # to ensure all words and the puzzle key fit on one page
            info_font_size = config.pdf_font_size_XL - (
                len(game.words) - config.min_puzzle_words
            ) * (6 / (config.max_puzzle_words - config.min_puzzle_words))
            pdf.set_font_size(font_size)

            # draw the puzzle
            if solution:
                placed_words_coordinates = {
                    coord
                    for coords in [
                        word.offset_coordinates(game.bounding_box)
                        for word in game.placed_words
                    ]
                    for coord in coords  # type: ignore
                }  # type: ignore
            else:
                placed_words_coordinates = {}  # type: ignore
            for y, row in enumerate(game.cropped_puzzle):
                for x, char in enumerate(row):
                    # change text color for correct letters if solution was requested
                    if solution and (x + 1, y + 1) in placed_words_coordinates:
                        pdf.set_text_color(255, 0, 0)
                        pdf.cell(
                            gsize,
                            gsize,
                            char.lower() if lowercase else char,
                            align="C",
                        )
                        pdf.set_text_color(0, 0, 0)
                    else:
                        pdf.cell(
                            gsize,
                            gsize,
                            char.lower() if lowercase else char,
                            align="C",
                        )
                pdf.ln(gsize)
            pdf.ln(0.25)

            # collect puzzle information
            word_list_str = utils.get_word_list_str(game.key)
            level_dirs_str = utils.get_level_dirs_str(game.level)
            key_intro = (
                "Answer Key (*Secret Words)"
                if game.placed_secret_words
                else "Answer Key"
            )
            answer_key_str = utils.get_answer_key_str(
                game.placed_words, game.bounding_box
            )

            # lower case was requested change case or letters for puzzle, words, and key
            if lowercase:
                word_list_str = word_list_str.lower()
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
                txt=f"Find words going {level_dirs_str}:",
                align="C",
                new_y="NEXT",
            )
            pdf.ln(0.125)

            # write word list
            pdf.set_font("Helvetica", "B", size=info_font_size)
            pdf.set_font_size(info_font_size)
            pdf.multi_cell(
                pdf.epw,
                info_font_size / 72 * 1.125,
                word_list_str,
                align="C",
                new_y="NEXT",
            )

            # write the puzzle answer key
            # resetting the margin before rotating makes layout easier to figure
            pdf.set_margin(0)
            # rotate the page to write answer key upside down
            with pdf.rotation(angle=180, x=pdf.epw / 2, y=pdf.eph / 2):
                pdf.set_xy(pdf.epw - pdf.epw, 0)
                pdf.set_margin(0.25)
                pdf.set_font("Helvetica", size=config.pdf_font_size_S)
                pdf.write(txt=f"{key_intro}: {answer_key_str}")

            return pdf

        # setup the PDF document
        pdf = FPDF(orientation="P", unit="in", format="Letter")
        pdf.set_author(config.pdf_author)
        pdf.set_creator(config.pdf_creator)
        pdf.set_title(config.pdf_title)
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
        game: Game,
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
        level_dirs_str = utils.get_level_dirs_str(game.level)
        key_intro = (
            "Answer Key (*Secret Words)" if game.placed_secret_words else "Answer Key"
        )
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
        output += f"* Words can go {level_dirs_str}\n\n"
        output += f"{key_intro}: {answer_key_str}"
        return output

    def highlight_solution(self, game: Game) -> Puzzle:
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
        game: Game,
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
