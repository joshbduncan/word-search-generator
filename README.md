# Word-Search-Generator

Word-Search-Generator is a Python module for generating fun [Word Search Puzzles](https://en.wikipedia.org/wiki/Word_search).

[![Tests](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/joshbduncan/word-search-generator/actions/workflows/tests.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/word-search-generator) [![PyPI version](https://badge.fury.io/py/word-search-generator.svg)](https://badge.fury.io/py/word-search-generator)

![WordSearch Generator](https://user-images.githubusercontent.com/44387852/209227303-4289957f-ade1-44d9-a0c7-5b860ef446cf.gif)

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

## Options

If you dig deep enough, you'll notice this package is completely overkill... There are numerous options and lots of possibilities. You can learn more by viewing the source code or checking out the project [Wiki](https://github.com/joshbduncan/word-search-generator/wiki).

👀 Wanna see it?

```pycon
>>> puzzle.show()  # or print(puzzle)
---------------------------
        WORD SEARCH
---------------------------
A G W K F B P V C U F U H R
B O I E U H W M I V P D K E
H N G S B P S J L N E Y X C
I J H V E G Y A X S T K J Q
F V Q E H F V E R B V A X K
U E H L A N I O K D J L T A
K S V P S C H C L O G D R F
Z F K I D N J D V N O P N D
C D N G T Y C N U K A I Q W
S O E Q V D B P I E T S M Y
X N T U R T L E G Y R K E K
T S I P I C T O R N S H O U
H U Q X M A D I G K T V C E
N T N I C I Q W M Q C I H P

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go E, SE, NE, and, S.

Answer Key: CAT NE @ (5, 14), DOG NE @ (7, 13), DONKEY S @ (10, 6), GOAT S @ (11, 7), HORSE NE @ (7, 7), PIG S @ (4, 7), SHEEP NE @ (2, 7), TURTLE E @ (3, 11)
```

ℹ️ The answer key uses 1-based indexing and a familiar (x, y) coordinate system. Directions are cardinal from first letter to last. \* Please note that all key values inside of the api are 0-based.

🍰 Too easy? Up the difficulty level.

```pycon
>>> puzzle.level = 3
>>> puzzle.show()
---------------------------
        WORD SEARCH
---------------------------
A G W K F B P V C U F U H R
B O I E U H W M I V P D K E
H N G S B P S J L N E Y X C
I J H V E G Y A X S T K J Q
F V Q E H F V E R B V A X K
U E H L A N I O K D J L T A
K S V P S C H C L O G D R F
Z F K I D N J D V N O P N D
C D N G T Y C N U K A I Q W
S O E Q V D B P I E T S M Y
X N T U R T L E G Y R K E K
T S I P I C T O R N S H O U
H U Q X M A D I G K T V C E
N T N I C I Q W M Q C I H P

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go SE, E, N, W, SW, NE, S, and, NW.

Answer Key: CAT NE @ (5, 14), DOG NE @ (7, 13), DONKEY S @ (10, 6), GOAT S @ (11, 7), HORSE NE @ (7, 7), PIG S @ (4, 7), SHEEP NE @ (2, 7), TURTLE E @ (3, 11)
```

🎛 Want a custom level?

Specify custom cardinal directions for your puzzle words (e.g. N, NE, E, SE, S, SW, W, NW).

```pycon
>>> puzzle.directions = "NW,SW"
>>> puzzle.show()
---------------------------
        WORD SEARCH
---------------------------
M L N C W X Q S V M G I A F
D J A T F O H J E Q R D C U
C T U L G E A G A Z O Z G R
O M O A E H Y M D G P O I B
W H Z P O Q F O I Q A B Y P
K J O R G C N M F T Z N T L
W Z S Q J K E D Q V Y U R W
F E C D E X N P L D R I L K
G K I Y F Z J S J T M P E V
Z M G P V N W G L C F H F W
S Q O E L F A E I H E Q X T
V I V P H X D Q Z P T M P O
F A D G O R L F Y J B X K E
H G M S Z B D M W M R L H N

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go SW, and, NW.

Answer Key: CAT SW @ (4, 1), DOG SW @ (12, 2), DONKEY SW @ (9, 4), GOAT SW @ (13, 3), HORSE SW @ (6, 4), PIG NW @ (10, 12), SHEEP SW @ (8, 1), TURTLE SW @ (13, 6)
```
😱 Still too easy? Go expert mode.

```pycon
>>> from word_search_generator import WordSearch
>>> puzzle = WordSearch(level=3)
>>> puzzle.random_words(10, secret=True, reset_size=True)
```

😓 Too hard? Go the easy route with `puzzle.level = 1` or `puzzle.directions = "E"`.

🎭 How about adding a mask ([docs](https://github.com/joshbduncan/word-search-generator/wiki/Puzzle-Masking))? ...Fancy!

```pycon
>>> from word_search_generator.mask.shapes import Heart
>>> puzzle.apply_mask(Heart())
>>> puzzle.show()
-------------------------
       WORD SEARCH
-------------------------
    C L C       C Y E
  Q S T N S   T E L D K
Z L O Z T P A K T H N M W
C C L Q C O N R S P Z V U
M I X V G O U R H S Z C H
  M H K D T T L E C U Q
  H C T H O R S E B M
    Z I S W R B P E G
      Y P I G B X Q
        C A T N G
        A R W O
          K D Q
            A

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go S, NE, E, and, SE.

Answer Key: CAT E @ (5, 10), DOG NE @ (7, 12), DONKEY NE @ (5, 6), GOAT NE @ (5, 5), HORSE E @ (5, 7), PIG E @ (5, 9), SHEEP S @ (9, 4), TURTLE NE @ (6, 6)
```

💾 Save your AWESOME puzzle as a PDF.

```pycon
>>> puzzle.save(path="~/Desktop/puzzle.pdf")
>>> "~/Desktop/puzzle.pdf"
```

## 🖥 CLI Integration

You can play WordSearch in your CLI too ([docs](https://github.com/joshbduncan/word-search-generator/wiki/Command-Line-Interface-(CLI)))! WordSearch Generator installs the console entry-point `word-search` so you can interact with the package right in your console.

```bash
$ word-search -r 10 -s 15 -l 3
-----------------------------
         WORD SEARCH
-----------------------------
J W X O X N A Q C A Q Z D R G
F B D M Y S E L F Z F N A K F
G K N E Q H D O P X Y T I G Z
V F C F T Y F Z S U E N D Y J
W A X P C K L B T B D I X T C
Y R C J Y P G R M L R V C O E
D K H Z C V Y I Z Q H B I P X
W U J D O S H N M T S O A U Q
L K C E M L V G S L F H F R Z
A F L Y A J K N F Z A Z T P D
E K P E Z P R M B P W C E O M
D N J G Y E F T H E S E R S J
B X Z P D B A B Y T C W J E F
E G L O F X E X P U P O V N A
M I M J Y S F N C H C F R P K

Find these words: AFTER, BABY, BRING, DEAL, KIND, MODERN, MYSELF, PURPOSE, RATE, THESE
* Words can go N, S, SW, W, E, NW, NE, and, SE.

Answer Key: AFTER S @ (13, 8), BABY E @ (6, 13), BRING S @ (8, 5), DEAL N @ (1, 12), KIND SW @ (14, 2), MODERN NE @ (3, 15), MYSELF E @ (4, 2), PURPOSE S @ (14, 7), RATE SW @ (14, 1), THESE E @ (8, 12)
```

## 📔 Documentation

If you need more info, most of the fun parts of Word-Search-Generator are documented on Github in the [Project Wiki](https://github.com/joshbduncan/word-search-generator/wiki).

Happy WordSearching ✌️
