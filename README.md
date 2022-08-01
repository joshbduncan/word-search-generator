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
-------------------
    WORD SEARCH
-------------------
B T Z L K J C G E H
X O N D G S W X M B
W H P V O E H Q D N
K G D I S G D C J G
C J Y R G W F A H O
M K O X N U K T F A
C H T U R T L E I T
D O N K E Y H C R M
V R T U X G O L W H
H J D G S H E E P Y

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go NE, E, SE, and S.

Answer Key: CAT S @ (4, 8), DOG SE @ (2, 4), DONKEY E @ (8, 1), GOAT S @ (4, 10), HORSE NE @ (7, 2), PIG SE @ (3, 3), SHEEP E @ (10, 5), TURTLE E @ (7, 3)
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
       SOLUTION
-----------------------
• • • • • • • C D H P •
• • • • • • • A O O I •
• • • • • D • T N R G •
• • • • • O • • K S • •
• • • • • G • • E E • •
• • • • • • • G Y • • •
• • • • • • • O • • • •
• • S H E E P A • • • •
• • • • T U R T L E • •
• • • • • • • • • • • •
• • • • • • • • • • • •
• • • • • • • • • • • •
```

🍰 Too easy? Up the difficulty level with `puzzle.level = 3`.

```
-----------------------
      WORD SEARCH
-----------------------
P X Y F L S O C Z R G R
H M S G O A T Y N T J N
G E C R S H U B O K X Y
T N Z I O C P H Y L W H
A J W R T M I E K T Y D
C X S Z A S G Y E U C E
P E C N F X E L D H B L
V T J I G K R K O M S T
L C H Y N H I N G Z W R
K Z A O F G E Y E N V U
R X D T V Y S U P F J T
C A M R U R P H E X K D

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE

* Words can go N, NE, E, SE, S, SW, W, and NW.

Answer Key: CAT N @ (6, 1), DOG S @ (7, 9), DONKEY NE @ (11, 3), GOAT E @ (2, 4), HORSE SW @ (3, 6), PIG S @ (4, 7), SHEEP NW @ (8, 11), TURTLE N @ (11, 12)
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

By default, the puzzle (characters) size is determined by the amount of words provided and the difficulty level. Need a puzzle an exact size, override the default with `puzzle.size = x` (25 >= integer >= 10). All puzzles are square so size` will be the width and height.

```
-----------------------
      WORD SEARCH
-----------------------
T M Y T U R T L E T O A
Y B V D L S A J X C K G
J Z K A T B N K U N R L
K U F V R K C G D H J T
P Q P I G P N V O Z G S
X C G J N Y A B N F O H
G A X L C G T J K U A E
O T R B H E O X E L T E
G A D Y M S C U Y Q K P
R X O N K Z H O R S E C
Y Q G H G F M U K L Z B
H W T C P W S X N U D N

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE

* Words can go E, and S.

Answer Key: CAT S @ (6, 2), DOG S @ (9, 3), DONKEY S @ (4, 9), GOAT S @ (5, 11), HORSE E @ (10, 7), PIG E @ (5, 3), SHEEP S @ (5, 12), TURTLE E @ (1, 4)
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

Word-Search-Generator can save puzzles as PDF and CSV files.

💾 Save a PDF to a specific directory with default filename.

```python
puzzle.save(path="~/Desktop/puzzle.pdf")
"~/Desktop/puzzle.pdf"
```

💾 Save a CSV with to the current directory with a specific filename.

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
usage: word-search [-h] [-r RANDOM] [-l {1,2,3}] [-s SIZE] [-o OUTPUT] [words ...]

Generate Word Search Puzzles!

positional arguments:
  words                 Words to include in the puzzle

options:
  -h, --help            show this help message and exit
  -r RANDOM, --random RANDOM
                        Generate {n} random words to include in the puzzle
  -l {1,2,3}, --level {1,2,3}
                        Difficulty level (1) beginner, (2) intermediate, (3) expert
  -s SIZE, --size SIZE  Puzzle size >=10 and <=25
  -o OUTPUT, --output OUTPUT
                        Output path for saved puzzle. Specify export type by appending '.pdf' or '.csv' to your path (defaults to PDF)

Copyright 2021 Josh Duncan (joshd.xyz)
```

💻 Generate a puzzle.

    $ word-search works, in, the, terminal, too

💻 Generate a puzzle **20 characters wide** with **difficulty level 1**.

    $ word-search works, in, the, terminal, too -l 1 -s 20

💻 Generate a puzzle with **10 random dictionary words**.

    $ word-search -r 10

💻 Generate a puzzle and **save as a pdf**.

    $ word-search works, in, the, terminal, too -o ~/Desktop/puzzle.pdf

💻 Generate a puzzle and **save as a csv**.

    $ word-search works, in, the, terminal, too -o puzzle.csv

ℹ️ You can also use words from a file...

```bash
$ cat words.txt | word-search
```

This really came in handy for those kid's food menus. I was able to take a folder full of .txt documents with themed words and generate dozens of level 1 Word Search Puzzles at exactly 15 characters in size super fast...

```bash
$ for f in tests/word*.txt; do word-search "$(cat $f)" -l 1 -s 15 -o $f.pdf; done
Puzzle saved: ~/.../puzzles/words-theme01.txt
...
Puzzle saved: ~/.../puzzles/words-theme99.txt
```

## Resources

-   [PyPi](https://pypi.python.org/pypi/word-search-generator)
