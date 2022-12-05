# CLI Integration

You can play or quick game or do some pretty impressive things with the Word-Search-Generator [CLI Integration](../reference/cli.md).

Generate a puzzle.

```
$ word-search works, from, the, cli, too
```
Generate a puzzle **20 characters wide** with **difficulty level 1**.

```
$ word-search works, from, the, cli, too -l 1 -s 20
```
Generate a puzzle with **10 random dictionary words**.

```
$ word-search -r 10
```
Generate a puzzle and **save as a csv**.

```
$ word-search works, from, the, cli, too -o puzzle.csv
```
Generate a puzzle and **save as a pdf** with the solution puzzle included.

```
$ word-search works, from, the, cli, too -o ~/Desktop/puzzle.pdf -c
```
ℹ️ You can also use words from a file...

```
$ cat words.txt | word-search
```

This really came in handy for those kid's food menus I mentioned in the introduction. I was able to take a folder full of .txt documents with themed words and generate dozens of level 1 Word Search Puzzles at exactly 15 characters in size super fast...

```
$ for f in tools/sample_word_lists/word*.txt; do word-search "$(cat $f)" -l 1 -s 15 -o $f.pdf; done
Puzzle saved: ~/.../words-5.txt.pdf
...
Puzzle saved: ~/.../words-50.txt.pdf
```

## CLI Expert Mode

Really want to challenge yourself? Try this in the CLI. All words will be secret, just don't peek 🫣 at the key! Good luck!

```bash
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
