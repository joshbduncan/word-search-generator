Word-Search-Generator is a Python package for generating fun [Word Search Puzzles](https://en.wikipedia.org/wiki/Word_search).

[![Tests](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/word-search-generator) [![PyPI version](https://badge.fury.io/py/word-search-generator.svg)](https://badge.fury.io/py/word-search-generator)

<p align="center"><img src="https://raw.githubusercontent.com/joshbduncan/word-search-generator/main/files/word-search.gif"/></p>

Like most of my programming endeavors, Word-Search-Generator was born out of necessity. I needed an easy way to generate a bunch of word search puzzles for kids' food menus at the day job.

🤦‍♂️ Does the world need this? Probably not.  
⏰ Did I spend way too much time on it? Yep!  
✅ Does it come in handy? Heck yeah!  
👍 Did I have fun making it? Absofreakinglutly!

## Installation

Install Word-Search-Generator with `pip`:

    $ pip install word-search-generator

## Usage

Just import the WordSearch class from the package, supply it with a list of words and you're set. 🧩

```pycon
>>> from word_search_generator import WordSearch
>>> puzzle = WordSearch("dog, cat, pig, horse, donkey, turtle, goat, sheep")
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

ℹ️ The answer key uses 1-based indexing and a familiar (x, y) coordinate system. Directions are cardinal from the first letter to the last. \* Please note that all key values inside of the API are 0-based.

🤷‍♂️ Can't find all of the words? You can view the answer key or highlight the hidden words in the output with `puzzle.show(solution=True)` 🔦.

![Show Puzzle With Highlighted Solution](https://user-images.githubusercontent.com/44387852/209019231-d0f8d659-3619-44c3-b199-81cd5a97a797.png)

If you dig deep enough, you'll notice this package is completely overkill... There are numerous options and lots of possibilities for its use. You can learn more by viewing the source code or checking out the project [Wiki](https://github.com/joshbduncan/word-search-generator/wiki).

Happy WordSearching ✌️

# Contributors

- Josh Duncan [@joshbduncan](https://github.com/joshbduncan)
- Chris J.M. [@duck57](https://github.com/duck57)
