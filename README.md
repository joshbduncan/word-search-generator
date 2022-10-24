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

👀 Wanna see it?

```pycon
>>> puzzle.show()  # or print(puzzle)
-----------------------
      WORD SEARCH
-----------------------
Z T G H X Z D B A G S E
X U S O M W O Z E B H L
B R Y R P G N T W F E R
J T G S K X K R V G E T
D L N E T D E F Q O P U
N E V O L C Y X V L Z L
C O A P R Q S Q B S W V
A T G E F C A T N H J D
E Z O J X Z U B D V B R
S Q A M G P I G Q C G Y
X V T R J E F W I E R N
D O G Y H R S B V L S O

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go S, and E.

Answer Key: CAT E @ (6, 8), DOG E @ (1, 12), DONKEY S @ (7, 1), GOAT S @ (3, 8), HORSE S @ (4, 1), PIG E @ (6, 10), SHEEP S @ (11, 1), TURTLE S @ (2, 1)
```

ℹ️ The answer key uses 1-based indexing and a familiar (x, y) coordinate system. Directions are cardinal from first letter to last. \* Please note that all key values inside of the api are 0-based.

🤷‍♂️ Can't find all of the words? You can view the answer key or highlight the hidden words in the output with `puzzle.show(solution=True)` 🔦.

```python
>>> puzzle.key
{'SHEEP': {'start': Position(row=0, column=10), 'direction': 'S', 'secret': False},
 'DONKEY': {'start': Position(row=0, column=6), 'direction': 'S', 'secret': False},
 'PIG': {'start': Position(row=9, column=5), 'direction': 'E', 'secret': False},
 'CAT': {'start': Position(row=7, column=5), 'direction': 'E', 'secret': False},
 'GOAT': {'start': Position(row=7, column=2), 'direction': 'S', 'secret': False},
 'DOG': {'start': Position(row=11, column=0), 'direction': 'E', 'secret': False},
 'TURTLE': {'start': Position(row=0, column=1), 'direction': 'S', 'secret': False},
 'HORSE': {'start': Position(row=0, column=3), 'direction': 'S', 'secret': False}}
```

🍰 Too easy? Up the difficulty level.

```pycon
>>> puzzle.level = 3
>>> puzzle.show()
-----------------------
      WORD SEARCH
-----------------------
W H Q Z M N M B P L F W
K Y K P D O L V A I N I
R X V E I C J C Z L M A
E Z H J O G F B J I G V
L F D Y E K N O D Y X F
E T I U Z O M T A C I E
D Q G M L B P E E H S X
I X W O H O R S E N C D
C M U R A K M Y C P I N
W P Y I C T C X O Y A K
Q D O G R N V E P F V C
Z F A C B E L T R U T A

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go N, SW, NW, SE, E, NE, W, and S.

Answer Key: CAT W @ (10, 6), DOG E @ (2, 11), DONKEY W @ (9, 5), GOAT SE @ (3, 7), HORSE E @ (5, 8), PIG SE @ (4, 2), SHEEP W @ (11, 7), TURTLE W @ (11, 12)
```

ℹ️ You'll find preset numeric levels listed in [config.py](/src/word_search_generator/config.py), each with specific cardinal directions that words can travel.

You can also specify custom cardinal directions for your puzzle (e.g. N, NE, E, SE, S, SW, W, NW).

```pycon
>>> puzzle.directions = "NW,SW"
>>> puzzle.show()
-----------------------
      WORD SEARCH
-----------------------
O I Y O T F J F M R L R
K W R D C W E N G S H V
N P S W M K I S U M D P
E F A L O D T Z R O H D
X H Q P G U B U G O O B
J R C E R A S L H N H P
Q Y I T V H Z Y K Q I C
R W L T E P T E S G X F
A E A E A Q Y A R A L O
J H P Y C O P W C Y B D
A V I E L R G X U J G A
W C X H D I N V K L W Y

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go SW, and NW.

Answer Key: CAT NW @ (9, 10), DOG SW @ (11, 3), DONKEY SW @ (12, 4), GOAT NW @ (7, 11), HORSE NW @ (11, 6), PIG SW @ (12, 6), SHEEP SW @ (7, 6), TURTLE SW @ (7, 4)
```
😱 Still too easy? Go expert mode. [Works in the CLI too](#expert-mode-cli)!

```pycon
> from word_search_generator import WordSearch
> from word_search_generator.utils import get_random_words
> puzzle = WordSearch(secret_words=get_random_words(10), level=3,)
```

ℹ️ You'll notice the `get_random_words()` function from the utils module used above. It generates {n} number of random words from a list of approximately 1000 American English dictionary words.

😓 Too hard? Go the easy route with `puzzle.level = 1` or `puzzle.directions = "E"`.

## Settings

Word-Search-Generator offers a few options for puzzle generation.

```pycon
>>> help(WordSearch.__init__)
Help on function __init__ in module word_search_generator:

__init__(self, words: Optional[str] = None, level: Union[int, str, NoneType] = None, size: Optional[int] = None, secret_words: Optional[str] = None, secret_level: Union[int, str, NoneType] = None)
    Initialize a Word Search puzzle.

    Args:
        words (Optional[str], optional): A string of words separated by spaces,
            commas, or new lines. Will be trimmed if more. Defaults to None.
        level (Optional[int  |  str], optional): Difficulty level or potential
            word directions. Defaults to 1.
        size (Optional[int], optional): Puzzle size. Defaults to None.
        secret_words (Optional[str], optional): A string of words separated by
            spaces, commas, or new lines. Words will be 'secret' meaning they
            will not be included in the word list. Defaults to None.
        secret_level (Optional[int  |  str], optional): Difficulty level or
            potential word directions for 'secret' words. Defaults to None.
```

```python
words = "dog, cat, pig, horse, donkey, turtle, goat, sheep"
puzzle = WordSearch(words, level=3, size=25)
```

⚠️ Anytime puzzle settings are adjusted, an entirely new puzzle will be generated!

### Words

A word search puzzle wouldn't be much without words... Puzzle words can be provided at time of creation or added after the fact. Words can be separated by spaces, commas, or new lines and Word-Search-Generator will sort them out for you.

```python
puzzle = WordSearch("some random words to hide")  # separated by a space
```

#### Editing Current Puzzle Words

🤦‍♂️ Leave out a word?

```python
puzzle.add_words("new, words, to, add")
```

❌ Need to remove a word?

```python
puzzle.remove_words("words, to, delete")
```

♻️ Replace all of the words?

```python
puzzle.replace_words("replace, current, words, with, new, words")
```

⚠️ When words are added, removed, or replaced, an entirely new puzzle will be generated!

### Level

Word-Search-Generator offers some preset difficulty levels. Some levels only allow for words to be placed left-to-right and others allow for right-to-left. You can find all of the preset numeric levels listed in [config.py](/src/word_search_generator/config.py).

```python
puzzle.level = 2
```

⚠️ Preset levels were the introduced in the first implementation of Word-Search-Generator for ease-of-use but have since been quasi-rolled in to the directions property. They will continue to be supported for backward compatibility.

### Size

By default, the puzzle size (in characters) is determined by the amount of words provided and the difficulty level. Need a puzzle an exact size, override the default by setting `puzzle.size`. All puzzles are square so size will be the width and height.

```pycon
>>> puzzle.size = 55
ValueError: Puzzle size must be >= 5 and <= 50
>>> puzzle.size = 20
```

ℹ️ Puzzles are limited to 50 characters wide so that everything fits nicely on a US Letter or A4 sized sheet of paper.

⚠️ All provided words may not fit a specified puzzle size!

### Secret Words

Word-Search-Generator accepts "secret" bonus that can up the difficulty of your puzzle. Secret words are not included in the word list and can have their own level or directions.

```pycon
>>> puzzle = WordSearch("dog, cat, pig", level=1, secret_words="secret, boo")
puzzle.show()
-----------------------
      WORD SEARCH
-----------------------
A U C Q X L H G C L K P
V K J A M D Y I N V S A
U M U Y J B O O M J N X
H D O Z F H Y Z B G S G
R U M A P D O G N U E P
B O P H B I C F J T C I
T J G K R V Y N X Q R G
S F U J P U K L I B E B
P H S K B F Y J Q C T X
G T L E P C N G U A K F
S H K H L D J I S T E O
P F P N Q C T D Q A K R

Find these words: CAT, DOG, PIG
* Words can go E, and S.

Answer Key: *BOO E @ (6, 3), CAT S @ (10, 9), DOG E @ (6, 5), PIG S @ (12, 5), *SECRET S @ (11, 4)
```

ℹ️ Secret words **ARE** included in the puzzle key (denoted by a '\*').

Secret words can also have their own level or set of directions.

```pycon
>>> puzzle.secret_directions="N,W"
-----------------------
      WORD SEARCH
-----------------------
X J G P N C R Q O J C O
G S F M G A N P M V Z Y
N H P D F T E T B N C Q
O C G T K Y D F U Y P Y
O K U E B T L C R S M T
B J X R D A R D O G Q J
Y N T C T K Z S R W Z E
B C D E P I P I G M U C
M W F S H C Z J D W N G
J Q X Y U N F V I V H V
S T N P Z C A O N B I Y
W A D H E W S B K A R K

Find these words: CAT, DOG, PIG
* Words can go E, and S.

Answer Key: *BOO N @ (1, 6), CAT S @ (6, 1), DOG E @ (8, 6), PIG E @ (7, 8), *SECRET N @ (4, 9)
```

⚠️ You may have noticed above that the secret directions are not included in the puzzle directions unless they overlap with the valid directions for the regular puzzle words. I told you it ups the difficulty level 📈.

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

```bash
$ word-search dog, cat, pig, horse -k > puzzle.txt
```

📁 **View Sample Files:**
[Word-Search PDF](/files/puzzle.pdf), [Word-Search CSV](/files/puzzle.csv), [Word-Search TXT](/files/puzzle.txt)

## CLI Integration

Word-Search-Generator works in your terminal too! 🙌

```
$ word-search -h
usage: word-search [-h] [-r RANDOM] [-x SECRET_WORDS | -rx RANDOM_SECRET_WORDS] [-d DIFFICULTY]
                   [-xd SECRET_DIFFICULTY] [-s SIZE] [-c] [-o OUTPUT] [--version]
                   [words ...]

Generate Word Search Puzzles!

Valid Levels: 1, 2, 3, 4, 8, 7
Valid Directions: N, NE, E, SE, S, SW, W, NW
* Directions are to be provided as a comma-separated list.

positional arguments:
  words                 Words to include in the puzzle (default: stdin).

options:
  -h, --help            show this help message and exit
  -r RANDOM, --random RANDOM
                        Generate {n} random words to include in the puzzle.
  -x SECRET_WORDS, --secret-words SECRET_WORDS
                        Secret bonus words not included in the word list.
  -rx RANDOM_SECRET_WORDS, --random-secret-words RANDOM_SECRET_WORDS
                        Generate {n} random secret words to include in the puzzle.
  -d DIFFICULTY, --difficulty DIFFICULTY, -l DIFFICULTY, --level DIFFICULTY
                        Difficulty level (numeric) or cardinal directions puzzle words can go. See valid arguments
                        above.
  -xd SECRET_DIFFICULTY, --secret-difficulty SECRET_DIFFICULTY
                        Difficulty level (numeric) or cardinal directions secret puzzle words can go. See valid
                        arguments above.
  -s SIZE, --size SIZE  Puzzle size >=5 and <=50
  -c, --cheat           Show the puzzle solution or include it within the `-o, --output` file.
  -o OUTPUT, --output OUTPUT
                        Output path for saved puzzle. Specify export type by appending '.pdf' or '.csv' to your path
                        (default: PDF).
  --version             show program's version number and exit

Copyright 2022 Josh Duncan (joshbduncan.com)
```

💻 Generate a puzzle.

```
$ word-search works, from, the, cli, too
```
💻 Generate a puzzle **20 characters wide** with **difficulty level 1**.

```
$ word-search works, from, the, cli, too -l 1 -s 20
```
💻 Generate a puzzle with **10 random dictionary words**.

```
$ word-search -r 10
```
💻 Generate a puzzle and **save as a csv**.

```
$ word-search works, from, the, cli, too -o puzzle.csv
```
💻 Generate a puzzle and **save as a pdf** with the solution puzzle included.

```
$ word-search works, from, the, cli, too -o ~/Desktop/puzzle.pdf -c
```
ℹ️ You can also use words from a file...

```
$ cat words.txt | word-search
```

This really came in handy for those kid's food menus. I was able to take a folder full of .txt documents with themed words and generate dozens of level 1 Word Search Puzzles at exactly 15 characters in size super fast...

```
$ for f in tools/sample_word_lists/word*.txt; do word-search "$(cat $f)" -l 1 -s 15 -o $f.pdf; done
Puzzle saved: ~/.../words-5.txt.pdf
...
Puzzle saved: ~/.../words-50.txt.pdf
```

### Expert Mode CLI

Really want to challenge yourself? Try this in the CLI. All words will be secret, just don't peek 🫣 at the key! Good luck!

```
$ word-search -rx 10 -l 3
-------------------
    WORD SEARCH
-------------------
M Y C K R E H T I E
I D A E R I G D G Y
N K H O K B N R S T
D J A V F H I E H G
G S R G T D H C B W
P N P W Q T T E V F
A V O T L U Y N M O
U R N O C P N T A U
G X C H K E A Q J R
M I D U N I W R O H

Find these words: <ALL SECRET WORDS>
* Words can go W, SW, NW, SE, E, N, NE, and S.

Answer Key: *ANYTHING N @ (7, 9), *EITHER W @ (10, 1), *FOUR S @ (10, 6), *GROWTH NE @ (1, 9), *HOT N @ (4, 9), *MIND S @ (1, 1), *PERFORMANCE None @ None, *PUT N @ (6, 8), *READ W @ (5, 2), *RECENT S @ (8, 3)
```

## Resources

- [PyPi](https://pypi.python.org/pypi/word-search-generator)
- [PyFPDF/fpdf2: Simple PDF generation for Python](https://github.com/PyFPDF/fpdf2)
- [Word search - Wikipedia](https://en.wikipedia.org/wiki/Word_search)


# Contributors

- Chris J.M. [@duck57](https://github.com/duck57)
