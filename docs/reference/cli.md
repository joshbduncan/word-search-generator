# Command Line Interface (CLI)

Word-Search-Generator works in your terminal too! 🙌

```bash
$ word-search dog cat pig
---------------------------
        WORD SEARCH
---------------------------
K A C X K S E F S R Y H Q Y
F L F I C Y M B C K Q U N C
Q M Y G N V P O Y P J B G J
E A I L Z H I K J D W N U S
P Q K F W X W S M V Z O V N
T A Z C O R O B N F M X Q T
B H D E M P S W G A S A G O
D R X V X H M U Y K U M B E
O V P D M K O P C P Z F Z O
G R W E R X D M N A S B P L
F T B D S G L P I G T O T U
H Z Y N K R V S E M D L B C
P S I A H X M G R J R W Z Q
M J V M D E Q W D V A T K A

Find these words: CAT, DOG, PIG
* Words can go NE, SE, S, and, E.

Answer Key: CAT SE @ (9, 9), DOG S @ (1, 8), PIG E @ (8, 11)
```

## CLI Help

```bash
$ word-search -h
usage: word-search [-h] [-c] [-d DIFFICULTY] [-im IMAGE_MASK | -m MASK_SHAPE]
                   [-o OUTPUT] [-r RANDOM] [-rx RANDOM_SECRET_WORDS] [-s SIZE]
                   [-pm] [-x SECRET_WORDS] [-xd SECRET_DIFFICULTY] [--version]
                   [words ...]

Generate Word Search Puzzles!

Valid Levels: 1, 2, 3, 4, 8, 7
Valid Directions: N, NE, E, SE, S, SW, W, NW
* Directions are to be provided as a comma-separated list.

positional arguments:
  words                 Words to include in the puzzle (default: stdin).

options:
  -h, --help            show this help message and exit
  -c, --cheat           Show the puzzle solution or include it within the `-o,
                        --output` file.
  -d DIFFICULTY, --difficulty DIFFICULTY, -l DIFFICULTY, --level DIFFICULTY
                        Difficulty level (numeric) or cardinal directions
                        puzzle words can go. See valid arguments above.
  -im IMAGE_MASK, --image-mask IMAGE_MASK
                        Mask the puzzle to a provided image (accepts: BMP,
                        JPEG, PNG).
  -m MASK_SHAPE, --mask MASK_SHAPE
                        Mask the puzzle to a shape (choices: Circle, Diamond,
                        Donut, Heart, Hexagon, Octagon, Pentagon, Star5,
                        Star6, Star8, Tree, Triangle).
  -o OUTPUT, --output OUTPUT
                        Output path for saved puzzle. Specify export type by
                        appending '.pdf' or '.csv' to your path (default:
                        PDF).
  -r RANDOM, --random RANDOM
                        Generate {n} random words to include in the puzzle.
  -rx RANDOM_SECRET_WORDS, --random-secret-words RANDOM_SECRET_WORDS
                        Generate {n} random secret words to include in the
                        puzzle.
  -s SIZE, --size SIZE  5 <= puzzle size <= 50
  -pm, --preview-masks  Preview all built-in mask shapes.
  -x SECRET_WORDS, --secret-words SECRET_WORDS
                        Secret bonus words not included in the word list.
  -xd SECRET_DIFFICULTY, --secret-difficulty SECRET_DIFFICULTY
                        Difficulty level (numeric) or cardinal directions
                        secret puzzle words can go. See valid arguments above.
  --version             show program's version number and exit

Copyright 2022 Josh Duncan (joshbduncan.com)
```

## Built-In Masks Shapes

Word-Search-Generator has an extensive puzzle masking module. Unfortunately it is beyond the scope of the CLI integration to implement all of the masking modules power but don't worry, I have included a bunch of pre-built mask shapes that can be applied with CLI arguments.

You can see all of the available masks with the `-pm/--preview-masks` flag.

```bash
$ word-search -pm
Circle
              * * * * * * *  
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
              * * * * * * *  

Diamond
                    *  
                  * * *  
                * * * * *  
              * * * * * * *  
            * * * * * * * * *  
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
            * * * * * * * * *  
              * * * * * * *  
                * * * * *  
                  * * *  
                    *  

Donut
              * * * * * * *  
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
* * * * * * * * *       * * * * * * * * *
* * * * * * * *           * * * * * * * *
* * * * * * *               * * * * * * *
* * * * * * *               * * * * * * *
* * * * * * *               * * * * * * *
* * * * * * * *           * * * * * * * *
* * * * * * * * *       * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
              * * * * * * *  

[(0, 7), (10, 20), (20, 7), (10, 3)]
Heart
      * * * * *           * * * * *  
    * * * * * * *       * * * * * * *  
  * * * * * * * * *   * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
          * * * * * * * * * * *  
            * * * * * * * * *  
              * * * * * * *  
                * * * * *  
                * * * * *  
                  * * *  
                    *  

Hexagon
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  

Octagon
          * * * * * * * * *  
        * * * * * * * * * * *  
      * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * *  
        * * * * * * * * * * *  
          * * * * * * * * *  

Pentagon
                    *  
                * * * * *  
              * * * * * * *  
            * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  

Star5
                    *  
                    *  
                  * * *  
                  * * *  
                * * * * *  
                * * * * *  
        * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
          * * * * * * * * * * *  
          * * * * * * * * * * *  
          * * * * * * * * * * *  
        * * * * * *   * * * * * *  
        * * * *           * * * *  
        * *                   * *  

Star6
                  *  
                * * *  
                * * *  
              * * * * *  
              * * * * *  
* * * * * * * * * * * * * * * * * * *
  * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
      * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * *
              * * * * *  
              * * * * *  
                * * *  
                * * *  
                  *  

Star8
                    *  
                    *  
                  * * *  
      * *         * * *         * *  
      * * * *   * * * * *   * * * *  
        * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * * * *
    * * * * * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
          * * * * * * * * * * *  
        * * * * * * * * * * * * *  
        * * * * * * * * * * * * *  
      * * * *   * * * * *   * * * *  
      * *         * * *         * *  
                  * * *  
                    *  
                    *  

Tree
                  *  
                * * *  
                * * *  
              * * * * *  
              * * * * *  
            * * * * * * *  
          * * * * * * * * *  
          * * * * * * * * *  
        * * * * * * * * * * *  
        * * * * * * * * * * *  
      * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * *
            * * * * * * *  
            * * * * * * *  
            * * * * * * *  
            * * * * * * *  
            * * * * * * *  

Triangle
                  *  
                * * *  
                * * *  
              * * * * *  
              * * * * *  
            * * * * * * *  
          * * * * * * * * *  
          * * * * * * * * *  
        * * * * * * * * * * *  
        * * * * * * * * * * *  
      * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
    * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
  * * * * * * * * * * * * * * * * *  
* * * * * * * * * * * * * * * * * * *
```
