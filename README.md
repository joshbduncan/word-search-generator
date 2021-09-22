# Word-Search-Generator

Word-Search-Generator is a Python module for generating fun [Word Search Puzzles](https://en.wikipedia.org/wiki/Word_search).

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

👀 Wanna see it? `puzzle.show()`

```
** WORD SEARCH **

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
```

Puzzle words can be provided as a string variable or directly as above. Words can be separated by spaces, commas, or new lines and Word-Search-Generator will sort them out for you.

🤷‍♂️ Can't finding all the words? Try, `puzzle.key`.

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

You can also show the key with the puzzle with `puzzle.show(key=True)`.

```
** WORD SEARCH **

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

🍰 Too easy? Up the difficulty level with `puzzle.level = 3`.

```
** WORD SEARCH **

Q B O I U A D G I P S I L N
V G U Z G O N C V C O Q D T
R I S B G O D U W M G V K R
K X O H W P A Z D J U H E T
H T B K R Y K T O X N O L Y
F I G E P D Q Z N W Y R T A
T B R H W R M U K O J S R S
O S X N F I J W E N X E U W
G A U S X T G N Y V A F T Y
I T O W J I V P A T J G O W
O B I Y D S E C L W C V T R
I H E O Q E P F J A K H C I
F Y W Z H Z Y L T L R U T A
I Z U S T M Q V O K W F E F

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go N, NE, E, SE, S, SW, W, and NW.
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

It's easy to set setting when creating a puzzle too...

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

By default, the puzzle (characters) size is determined by the amount of words provided and the difficulty level. Need a puzzle an exact size, override the default with `puzzle.size = x` (30 >= integer >= 10). All puzzles are square so size` will be the width and height.

```
** WORD SEARCH **

P I G O Z D U M Y D A F C N
T F L Q T P X I Q O W L A W
B P D K U Y M W Z N G S T B
L C L O R O Q G A K O H U P
M G S Z T J R N U E A E M H
Y T R I L W E Q S Y T E F N
I N K U E X D C U D X P B A
B F B F P V K I J P O E Y S
A L N I L H F G R S W Q M R
X Y Q E S C V W B E J X F K
Z D S T A J E X U C Y M I J
L I H G X W U N S D O G K E
S W D W C D G K A U N B T H
P M F V T W J L H O R S E P

Find these words: CAT, DOG, DONKEY, GOAT, HORSE, PIG, SHEEP, TURTLE
* Words can go E, and S.
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
puzzle.save(path="~/Desktop", format="pdf")
".../Desktop/Word Search 2021-01-01T000000.pdf"
```

💾 Save a CSV with to the current directory with a specific filename.

```python
puzzle.save(path="puzzle.csv", format="csv")
".../projects/word-search/puzzle.csv"
```

ℹ️ Using the Word-Search-Generator [CLI Integration](#cli-integration) and [redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) in your terminal you can also save the puzzle to a text file.

    $ word-search dog, cat, pig, horse -k > puzzle.txt

📁 **View Sample Files:**
[Word-Search PDF](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.pdf), [Word-Search CSV](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.csv), [Word-Search TXT](https://github.com/joshbduncan/word-search-generator/blob/main/files/puzzle.txt)

## CLI Integration

Word-Search-Generator works in your terminal too! 🙌

```
$ word-search -h
usage: word-search [-h] [-l {1,2,3}] [-s SIZE] [-k] [-t] [-e {csv,pdf}] [-o OUTPUT] [words ...]

Generate Word Search Puzzles!

positional arguments:
  words                 words to include in the puzzle

optional arguments:
  -h, --help            show this help message and exit
  -l {1,2,3}, --level {1,2,3}
                        difficulty level (1) beginner, (2) intermediate, (3) expert
  -s SIZE, --size SIZE  puzzle size >=10 and <=25
  -k, --key             show answer key
  -t, --tabs            use tabs as character separator
  -e {csv,pdf}, --export {csv,pdf}
                        export puzzle as 'csv' or 'pdf' file
  -o OUTPUT, --output OUTPUT
                        output path for '-e', '--export' flag
```

💻 Generate a puzzle.

    $ word-search works, in, the, terminal, too

💻 Generate a puzzle **20 characters wide** with **difficulty level 1**.

    $ word-search works, in, the, terminal, too -l 1 -s 20

💻 Generate a puzzle with **10 random dictionary words**.

    $ word-search -r 10

💻 Generate a puzzle and **save as a pdf**.

    $ word-search works, in, the, terminal, too -e pdf -o ~/Desktop

💻 Generate a puzzle and **save as a csv**.

    $ word-search works, in, the, terminal, too -e csv -o ~/Desktop/puzzle.csv

ℹ️ You can also use words from a file...

```bash
$ cat words.txt | word-search
```

This really came in handy for those kid's food menus. I was able to take a folder full of .txt documents with themed words and generate dozens of level 1 Word Search Puzzles at exactly 15 characters in size super fast...

```bash
$ for f in tests/word*.txt; do word-search "$(cat $f)" -l 1 -s 15 -e pdf -o $f.pdf; done
Puzzle saved: ~/.../puzzles/words-theme01.txt
...
Puzzle saved: ~/.../puzzles/words-theme99.txt
```

## Resources

-   [PyPi](https://pypi.python.org/pypi/word-search-generator)
