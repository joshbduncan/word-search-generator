# Word-Search-Generator

Word-Search-Generator is a Python module for generating fun [Word Search Puzzles](https://en.wikipedia.org/wiki/Word_search).

[![Tests](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/word-search-generator) [![PyPI version](https://badge.fury.io/py/word-search-generator.svg)](https://badge.fury.io/py/word-search-generator)

<p align="center"><img src="https://raw.githubusercontent.com/joshbduncan/word-search-generator/main/files/word-search.gif"/></p>

Like most of my programming endeavors, Word-Search-Generator was born out of necessity. I needed an easy way to generate a bunch of word search puzzles for kid's food menus at the day job.

🤦‍♂️ Does the world need this? Probably not.
⏰ Did I spend way too much time on it? Yep!
✅ Does it come in handy? Heck yeah!
👍 Did I have fun making it? Absofreakinglutly!

## Installation

Install Word-Search-Generator with `pip`:

    $ pip install word-search-generator

## Usage

Just import the WordSearch class from the package, supply it with a list of words and you're set. 🧩

```python
from word_search_generator import WordSearch

puzzle = WordSearch("dog, cat, pig, horse, donkey, turtle, goat, sheep")
```

👀 Wanna see it? `print(puzzle)` or `puzzle.show()`

```
-----------------------
      WORD SEARCH
-----------------------
T L Q D O N K E Y K M P
Z X R C V E J R S A H S
C Y V I T I O Q U X C D
A E P Z V C W J K D H P
T V G O A T H R E O O A
X Q P H S C I C S G R F
U J I N I H S U H K S O
F H G O Z J O A E D E I
B Z S H S E D H E I X R
H V P L U X Y B P Z U W
M W B G Q T U R T L E T
H X O U B M H S X W Q B

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go E, and S.

Answer Key: CAT S @ (2, 0), DOG S @ (3, 9), DONKEY E @ (0, 3), GOAT E @ (4, 2), HORSE S @ (3, 10), PIG S @ (5, 2), SHEEP S @ (5, 8), TURTLE E @ (10, 5)
```

ℹ️ The output answer key uses a 1-based index as that's more familiar with non-programmers. First number is the row, second is the column. Directions are cardinal from first letter to last. The stored `puzzle.key` is 0-based.

Puzzle words can be provided as a string variable or directly as above. Words can be separated by spaces, commas, or new lines and Word-Search-Generator will sort them out for you.

🤷‍♂️ Can't find all of the words? Try, `puzzle.key`...

```python
{"TURTLE": {"start": (7, 3), "direction": "E"},
 "PIG": {"start": (3, 3), "direction": "SE"},
 "HORSE": {"start": (7, 2), "direction": "NE"},
 "GOAT": {"start": (4, 10), "direction": "S"},
 "DOG": {"start": (2, 4), "direction": "SE"},
 "DONKEY": {"start": (8, 1), "direction": "E"},
 "SHEEP": {"start": (10, 5), "direction": "E"},
 "CAT": {"start": (4, 8), "direction": "S"}}
```

or show just the hidden words `puzzle.show(solution=True)`.

```
-----------------------
      WORD SEARCH
-----------------------
• • • D O N K E Y • • •
• • • • • • • • • • • •
C • • • • • • • • • • •
A • • • • • • • • D H •
T • G O A T • • • O O •
• • P • • • • • S G R •
• • I • • • • • H • S •
• • G • • • • • E • E •
• • • • • • • • E • • •
• • • • • • • • P • • •
• • • • • T U R T L E •
• • • • • • • • • • • •

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go E, and S.

Answer Key: CAT S @ (2, 0), DOG S @ (3, 9), DONKEY E @ (0, 3), GOAT E @ (4, 2), HORSE S @ (3, 10), PIG S @ (5, 2), SHEEP S @ (5, 8), TURTLE E @ (10, 5)
```

🍰 Too easy? Up the difficulty level with `puzzle.level = 3`.

```
-----------------------
      WORD SEARCH
-----------------------
J V W N B Y E K N O D U
G E B D F N H O R S E H
M I C K G Y F I D C P D
V H W A V H M Y O B G I
G O A T T C F U A S H K
X H U W K V O Y G V B O
G B Q A M Z X W O Z Y N
T M D P C A S B D E W E
L Y I E R W X G I P U C
C H U E C N Q C J L W O
F S X H G I V I P F A N
B J D S F M E L T R U T

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go N, NE, E, SE, S, SW, W, and NW.

Answer Key: CAT SE @ (2, 2), DOG N @ (7, 8), DONKEY W @ (0, 10), GOAT E @ (4, 0), HORSE E @ (1, 6), PIG W @ (8, 9), SHEEP N @ (11, 3), TURTLE W @ (11, 11)
```

😓 Too hard? Go the easy route with `puzzle.level = 1`.

## Settings

Word-Search-Generator offers two main options for puzzle generation, `level` and `size`.

```python
# Set the difficulty level to 2
puzzle.level = 2

# Set the puzzle size to 25
puzzle.size = 25
```

It's easy to define options when creating a puzzle too...

```python
words = "dog, cat, pig, horse, donkey, turtle, goat, sheep"
puzzle = WordSearch(words, level=3, size=25)
```

⚠️ Anytime puzzle settings are adjusted, an entirely new puzzle will be generated!

### Difficulty Level

The difficulty level controls whether words can go forward or backward, the cardinal direction they can go, and the size of the puzzle (unless `size` is explicitly set). Difficulty level defaults to 2.

-   **Level 1 (Easy)**: Words can go forward in directions EAST (E), or SOUTH (S). Puzzle size is small by default.
-   **Level 2 (Intermediate)**: Words can go forward in directions NORTHEAST (NE), EAST (E), SOUTHEAST (SE), or (S). Puzzle size is medium by default.
-   **Level 3 (Expert)**: Words can go forward and backward in directions NORTH (N), NORTHEAST (NE), EAST (E), SOUTHEAST (SE),
    SOUTH (S), SOUTHWEST (SW), WEST (W), or NORTHWEST (NW). Puzzle size is large by default.

### Puzzle Size

By default, the puzzle (characters) size is determined by the amount of words provided and the difficulty level. Need a puzzle an exact size, override the default with `puzzle.size = x` (25 >= integer >= 10). All puzzles are square so size will be the width and height.

```python
puzzle.size = 30
ValueError: Puzzle size must be >= 10 and <= 25
puzzle.size = 20
puzzle.show()
```

Puzzles are limited to 25 characters wide so that everything fits nicely on a US Letter or A4 sized sheet of paper.

```
---------------------------------------
              WORD SEARCH
---------------------------------------
T K U D Q X Z W J N K F N W C J K A M R
H A M H R O S C M E H G C K D R I L B O
I N S L X I D I V Z P N Q B S Q X P N V
Q U Z M V M P N P A C W X L F T S B X J
E V W H O R S E R L I E N R V W A Z S Q
N A K P M N F D F W U O F E F G T C F D
J X W N H B O K X P J I M A H L M Q W L
R Q S R E Z Y N C Q C N E I Z X Y C S N
M T H M V I S H E E P H F H J N D W B M
P B U F S M B Y O L I U B E R W Q I D K
J Z Y E J U X E C V E H C L M U P M W G
S N X M T F T K R I N G W T D C E H V N
B V Z N O K H N H V Z B P R V N L G M O
R M G E L B P O X U R T M U P Y A D I U
Y V T O I Q I D Z G A N S T K E M F E P
U D M K E V B H R O E Q O N M Z V Q B Y
R Q C N U R J V G S L J M R X F B R T J
Z F G L D W U R Z Y P W U O A H O X P Q
R O U P S T I O H Q S M X F S K P Z C D
D M K J M P E R X W G Z A V N F X B T J

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go N, NE, E, SE, S, SW, W, and NW.

Answer Key: CAT NW @ (5, 17), DOG NE @ (19, 0), DONKEY N @ (14, 7), GOAT NE @ (16, 8), HORSE E @ (4, 3), PIG NW @ (14, 19), SHEEP E @ (8, 6), TURTLE N @ (14, 13)
```

⚠️ All provided words may not fit a specified puzzle size!

## Editing Puzzle Words

Word-Search-Generator makes it easy to edit the words in the current puzzle.

🤦‍♂️ Leave out a word?

```python
puzzle.add_words("new, words, to, add")
```

❌ Need to remove a word?

```python
puzzle.remove_words("words, to, delete")
```

🗑 Wanna replace all words?

```python
puzzle.replace_words("replace, current, words, with, new, words")
```

⚠️ When words are added, removed, or replaced, an entirely new puzzle will be generated!

## Saving Puzzles

Word-Search-Generator can save puzzles as PDF and CSV files. The file format for which each puzzle is saved is derived from the file extension in the provided path name. Defaults to PDF is no file extension if provided.

💾 Save as a PDF.

```python
puzzle.save(path="~/Desktop/puzzle.pdf")
"~/Desktop/puzzle.pdf"
```

💾 Save as a CSV.

```python
puzzle.save(path="puzzle.csv")
"./puzzle.csv"
```

ℹ️ Using the Word-Search-Generator [CLI Integration](#cli-integration) and [redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) in your terminal you can also save the puzzle to a text file.

    $ word-search dog, cat, pig, horse -k > puzzle.txt

📁 **View Sample Files:**
[Word-Search PDF](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.pdf), [Word-Search CSV](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.csv), [Word-Search TXT](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.txt)

## CLI Integration

Word-Search-Generator works in your terminal too! 🙌

```
$ word-search -h
usage: word-search [-h] [-r RANDOM] [-l {1,2,3}] [-s SIZE] [-c] [-o OUTPUT] [--version] [words ...]

Generate Word Search Puzzles! (Version 1.3.0)

positional arguments:
  words                 Words to include in the puzzle

options:
  -h, --help            show this help message and exit
  -r RANDOM, --random RANDOM
                        Generate {n} random words to include in the puzzle
  -l {1,2,3}, --level {1,2,3}
                        Difficulty level (1) beginner, (2) intermediate, (3) expert
  -s SIZE, --size SIZE  Puzzle size >=10 and <=25
  -c, --cheat           Show the puzzle solution or include it within the `-o, --output` file.
  -o OUTPUT, --output OUTPUT
                        Output path for saved puzzle. Specify export type by appending '.pdf' or '.csv' to your path
                        (defaults to PDF)
  --version             show program's version number and exit

Copyright 2022 Josh Duncan (joshbduncan.com)
```

💻 Generate a puzzle.

    $ word-search works, in, the, terminal, too

💻 Generate a puzzle **20 characters wide** with **difficulty level 1**.

    $ word-search works, in, the, terminal, too -l 1 -s 20

💻 Generate a puzzle with **10 random dictionary words**.

    $ word-search -r 10

💻 Generate a puzzle and **save as a csv**.

    $ word-search works, in, the, terminal, too -o puzzle.csv

💻 Generate a puzzle and **save as a pdf** with the solution puzzle included.

    $ word-search works, in, the, terminal, too -o ~/Desktop/puzzle.pdf -c

ℹ️ You can also use words from a file...

```bash
$ cat words.txt | word-search
```

This really came in handy for those kid's food menus. I was able to take a folder full of .txt documents with themed words and generate dozens of level 1 Word Search Puzzles at exactly 15 characters in size super fast...

```bash
$ for f in tools/sample_word_lists/word*.txt; do word-search "$(cat $f)" -l 1 -s 15 -o $f.pdf; done
Puzzle saved: ~/.../words-5.txt.pdf
...
Puzzle saved: ~/.../words-50.txt.pdf
```

## Resources

- [PyPi](https://pypi.python.org/pypi/word-search-generator)
- [PyFPDF/fpdf2: Simple PDF generation for Python](https://github.com/PyFPDF/fpdf2)
- [Word search - Wikipedia](https://en.wikipedia.org/wiki/Word_search)
