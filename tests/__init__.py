from word_search_generator.mask.shapes import (
    Circle,
    Diamond,
    Donut,
    Heart,
    Hexagon,
    Octagon,
    Pentagon,
    Star5,
    Star6,
    Star8,
    Tree,
    Triangle,
)

ITERATIONS = 5
WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"
MASKS = [
    None,
    Circle(),
    Diamond(),
    Donut(),
    Heart(),
    Hexagon(),
    Octagon(),
    Pentagon(),
    Star5(),
    Star6(),
    Star8(),
    Tree(),
    Triangle(),
]
