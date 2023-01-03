from __future__ import annotations

from word_search_generator import WordSearch
from word_search_generator.utils import get_random_words


def main():
    puzzles = []
    # sizes = range(50, 51)
    # word_ct = range(10, 101)
    # quarter extremes
    sizes = [50]
    word_ct = [
        14,
        15,
        16,
        24,
        25,
        26,
        28,
        29,
        30,
        32,
        33,
        34,
        44,
        45,
        46,
        49,
        50,
        51,
        59,
        60,
        61,
        65,
        66,
        67,
        74,
        75,
        76,
        89,
        90,
        91,
        99,
        100,
    ]
    for size in sizes:
        for words in word_ct:
            wordlist = ",".join(get_random_words(words))
            p = WordSearch(wordlist, size=size)
            path = f"/Users/jbd/Desktop/PDF-Testing/test_{size}_{words}.pdf"
            print(f"{path=}")
            print(f"{len(p.words)=}")
            p.save(path, True)
            puzzles.append(p)
    print(f"Puzzles Created: {len(puzzles)}")


if __name__ == "__main__":
    main()
