# Quick Start

Just import the `WordSearch` class, supply it with a list of words, and you're set. 🧩

```pycon
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

🤷‍♂️ Can't find all of the words? You can highlight the hidden words in the output with `puzzle.show(solution=True)`.

![Show Puzzle With Highlighted Solution](../images/word-search-cli.png "Puzzle Show Highlighted Solution")
