"""
• • • • • • • • • E
• • • • • • • R • A
• • • • • • • A • T
• • • C • • • T • •
• • • A • • • • H •
B • • T • • • • A •
A • • • • • • • T •
T • • • • • • • • •
• • • • • • • • • •
• • • • • • • • • •
Answer Key: BAT S @ (6, 1), CAT S @ (4, 4), EAT S @ (1, 10), HAT S @ (5, 9), RAT S @ (2, 8)
"""

import copy
import random
import string
from collections import defaultdict
from word_search_generator import config


ALPHABET = list(string.ascii_uppercase)


words = {"BAT", "CAT", "EAT", "HAT", "RAT"}
s = [
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "E"],
    ["•", "•", "•", "•", "•", "•", "•", "R", "•", "A"],
    ["•", "•", "•", "•", "•", "•", "•", "A", "•", "T"],
    ["•", "•", "•", "C", "•", "•", "•", "T", "•", "•"],
    ["•", "•", "•", "A", "•", "•", "•", "•", "H", "•"],
    ["B", "•", "•", "T", "•", "•", "•", "•", "A", "•"],
    ["A", "•", "•", "•", "•", "•", "•", "•", "T", "•"],
    ["T", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
]
p = [
    ["W", "E", "G", "V", "Q", "L", "H", "N", "J", "E"],
    ["V", "R", "L", "T", "S", "W", "X", "R", "I", "A"],
    ["J", "Z", "K", "B", "M", "J", "V", "A", "F", "T"],
    ["W", "P", "Y", "C", "F", "O", "R", "T", "N", "V"],
    ["Z", "V", "U", "A", "E", "Y", "L", "U", "H", "S"],
    ["B", "G", "L", "T", "V", "P", "A", "Z", "A", "M"],
    ["A", "V", "A", "Y", "L", "Y", "V", "O", "T", "I"],
    ["T", "F", "J", "I", "R", "E", "T", "X", "Q", "F"],
    ["C", "I", "A", "T", "Q", "I", "D", "E", "V", "A"],
    ["O", "B", "S", "R", "S", "E", "R", "U", "C", "X"],
]


def out_of_bounds(width, height, pos):
    row, col = pos
    if row < 0 or col < 0 or row > height - 1 or col > width - 1:
        return True
    return False


def check_position_for_dupes(p, word, pos):
    size = len(p)
    matches = 0
    for rmove, cmove in config.dir_moves.values():
        check_row, check_col = pos
        matched = True
        for char in word:
            if out_of_bounds(size, size, (check_row, check_col)):
                matched = False
                break
            elif p[check_row][check_col] == char:
                check_row += rmove
                check_col += cmove
            else:
                matched = False
                break
        if matched:
            matches += 1
    if matches > 1:
        return True
    return False


def check_board_for_dupes(p, words):
    size = len(p)
    for row in range(size):
        for col in range(size):
            for word in words:
                if p[row][col] == word[0]:
                    if check_position_for_dupes(p, word, (row, col)):
                        return True
    return False


# print(check_board_for_dupes(p, words))
MISSED = 0


def check_point_old(p, c, pos, l, words):
    work_p = copy.deepcopy(p)
    size = len(work_p)
    words = []
    for rmove, cmove in config.dir_moves.values():
        row, col = pos
        letters = []
        for _ in range(l):
            letters.append(work_p[row][col])
            row += rmove
            col += cmove
            if out_of_bounds(size, size, (row, col)):
                break
        words.append("".join(letters))
        words.append("".join(letters[::-1]))
    print(words)


def no_matching_neighbors(puzzle, char, position):
    row, col = position
    # check all 8 possible neighbors
    for d in config.dir_moves:
        test_row = row + config.dir_moves[d][0]
        test_col = col + config.dir_moves[d][1]
        # if test coordinates are off puzzle skip
        if (
            test_row < 0
            or test_col < 0
            or test_row > len(puzzle) - 1
            or test_col > len(puzzle[0]) - 1
        ):
            continue
        # if this neighbor matchs try another character
        if char == puzzle[test_row][test_col]:
            return False
    return True


def fill_blanks(puzzle_solution, words):
    global MISSED
    puzzle = copy.deepcopy(puzzle_solution)
    # iterate over the entire puzzle
    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            # if the current spot is empty fill with random character
            if puzzle[row][col] == "•":
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_matching_neighbors(puzzle, random_char, (row, col)):
                        if check_point(puzzle, random_char, (row, col), words):
                            puzzle[row][col] = random_char
                            break
                        else:
                            print(f"random {random_char} didn't fit...")
                            MISSED += 1

    return puzzle


def check_point(p, c, pos, words):
    l = max([len(word) for word in words])
    work_p = copy.deepcopy(p)
    size = len(work_p)
    parts = []
    start_ct = change_ct = 0
    for rmove, cmove in config.dir_moves.values():
        row, col = pos
        letters = []
        for _ in range(l):
            letters.append(work_p[row][col])
            row += rmove
            col += cmove
            if out_of_bounds(size, size, (row, col)):
                break
        parts.append("".join(letters))
        for i, part in enumerate(parts[4:]):
            if parts[i][0] == "•":
                p1 = parts[i][::-1]
            else:
                p1 = parts[i]
            if part[-1] == "•":
                p2 = part[::-1]
            else:
                p2 = part
            r = p1 + p2[1:]
            for word in words:
                if word in r or word in r[::-1]:
                    start_ct += 1
                adjusted_r = r[: len(r) // 2] + c + r[len(r) // 2 + 1 :]
                if word in adjusted_r or word in adjusted_r[::-1]:
                    change_ct += 1
    if start_ct == change_ct:
        return True
    return False


p = [
    ["A", "B", "C", "D", "E"],
    ["F", "G", "H", "I", "J"],
    ["K", "L", "M", "N", "O"],
    ["P", "Q", "R", "S", "T"],
    ["U", "V", "W", "X", "Y"],
]

p = [
    ["A", "B", "A", "D", "E"],
    ["B", "G", "B", "I", "J"],
    ["K", "A", "•", "N", "O"],
    ["P", "Q", "T", "S", "T"],
    ["U", "V", "W", "X", "Y"],
]

# print(check_point(p, "A", (2, 2), {"AB", "TO", "BAT"}))
for i in range(10):
    print("\n", i, "\n")
    new_p = fill_blanks(s, words)
    for row in new_p:
        print(" ".join(row))
print(MISSED)


sample = [
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "I", "N", "T", "E", "R", "V", "I", "E", "W", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "T", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "O", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "P", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["M", "E", "N", "T", "I", "O", "N", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "C", "A", "R", "E", "•"],
    ["•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•", "•"],
]
