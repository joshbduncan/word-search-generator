# Puzzle Masking

Masks allow you to "mask" areas of a WordSearch puzzle, making those areas inactive for placing characters. There are many mask types but they all inherit from the base `Mask` object ([full API](base-object.md)).

* [Bitmap](bitmap.md)
* [Compound](compound.md)
* [Ellipse](ellipse.md)
* [Image](image.md)
* [Polygon](polygon.md)
* [Rectangle](rectangle.md)
* [Regular Polygon](regular-polygon.md)

The base mask class only has a few key properties, `Mask.method` and `Mask.static`.

### Mask().method

`Mask.method` determines how the mask is applied to the puzzle.

To best understand `Mask.method`, let me show what a sample mask looks like.

```pycon
>>> from word_search_generator.mask import Ellipse
>>> mask = Ellipse(11, 5)
>>> mask.generate(11)
>>> mask.show()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # #
# # * * * * * * * # #
* * * * * * * * * * *
* * * * * * * * * * *
* * * * * * * * * * *
# # * * * * * * * # #
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # #
```

As you can see in the output above, a mask (no matter the type) is made up of `ACTIVE` (\*) and `INACTIVE` (#) spaces. `ACTIVE` (\*) spaces will "act" on a puzzle depending on the `Mask.method`. If it helps, in the physical world, the above mask would be a square with an oval shape cut out of the middle, masking all of the areas marked `INACTIVE` (#), and revealing all of the areas marked `ACTIVE` (\*).

#### Method Types

**(1) Standard:** All `INACTIVE` (#) spaces from the mask will deactivate corresponding spaces on the current puzzle, intersecting with any previously applied masks.

```pycon
>>> p = WordSearch("dog cat pig", size=15)
>>> p.apply_mask(Ellipse(15, 7))
>>> p.show_mask()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # * * * * * * * # # # #
# * * * * * * * * * * * * * #
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
# * * * * * * * * * * * * * #
# # # # * * * * * * * # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
>>> p.apply_mask(Ellipse(7, 15, method=1))
>>> p.show_mask()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # * * * * * * * # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
```

Using the default standard method (`method=1`) on the second vertical oval mask, you can see that it interacts with the previous mask so only intersecting/overlapping areas are active on the puzzle.

**(2) Additive:** All `ACTIVE` (\*) spaces from the mask will activate corresponding spaces on the current puzzle, no matter the current puzzle state.

```pycon
>>> p = WordSearch("dog cat pig", size=15)
>>> p.apply_mask(Ellipse(15, 7))
>>> p.show_mask()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # * * * * * * * # # # #
# * * * * * * * * * * * * * #
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
# * * * * * * * * * * * * * #
# # # # * * * * * * * # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
>>> p.apply_mask(Ellipse(7, 15, method=2))
>>> p.show_mask()
# # # # # # * * * # # # # # #
# # # # # * * * * * # # # # #
# # # # # * * * * * # # # # #
# # # # # * * * * * # # # # #
# # # # * * * * * * * # # # #
# * * * * * * * * * * * * * #
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
# * * * * * * * * * * * * * #
# # # # * * * * * * * # # # #
# # # # # * * * * * # # # # #
# # # # # * * * * * # # # # #
# # # # # * * * * * # # # # #
# # # # # # * * * # # # # # #
```

Using the additive method (`method=2`) on the second vertical oval mask, you can see that it doesn't interact with the previous mask at all, it simply activates all of it's `ACTIVE` areas on the current puzzle.

**(3) Subtractive:** All `ACTIVE` (\*) spaces from the mask will deactivate corresponding spaces on the current puzzle, no matter the current puzzle state.

```pycon
>>> p = WordSearch("dog cat pig", size=15)
>>> p.apply_mask(Ellipse(15, 7))
>>> p.show_mask()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # * * * * * * * # # # #
# * * * * * * * * * * * * * #
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
* * * * * * * * * * * * * * *
# * * * * * * * * * * * * * #
# # # # * * * * * * * # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
>>> p.apply_mask(Ellipse(7, 15, method=3))
>>> p.show_mask()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# * * * # # # # # # # * * * #
* * * * # # # # # # # * * * *
* * * * # # # # # # # * * * *
* * * * # # # # # # # * * * *
# * * * # # # # # # # * * * #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
```

By using the subtractive method (`method=3`) on the second vertical oval mask, you can see that it doesn't interact with the previous mask at all, it simply deactivates all of its `ACTIVE` areas on the current puzzle.

### Mask().static

A `Puzzle` object retains all applied masks so that they can be reapplied if the puzzle size changes. Only masks marked as non static `Mask.static = False` will be reapplied. All masks are marked as `static=True` by default so users don't experience unexpected results when using many of the methods available on the `WordSearch` object.

This property exists because there are many masks types that are calculated for you based on the puzzle size so these masks can easily scale if adjust the puzzle. The problem arises when you create custom/non-calculated masks that can't be easily recalculated to fit on a different puzzle size. In this case (`Mask.static = True`) the mask will remain in `Puzzle.masks` but will not be re-applied when the puzzle size changes.

If you would like to remove all static masks from a puzzle, you can use the `remove_static_masks()` method. If you want to remove all masks from a puzzle (static or not), use the `remove_masks()` method.

### Applying Masks To A Puzzle

Masks can be applied individually to a `WordSearch` puzzle object using `apply_mask()` like above, or you can apply multiple masks all at once use the `apply_masks()` method.

```pycon
>>> p = WordSearch("dog cat pig", size=15)
>>> mask1 = (Ellipse(15, 7))
>>> mask2 = (Ellipse(7, 15, method=2))
>>> p.apply_masks([mask1, mask2])
>>> p.show_mask()
```

## Pre-Built Mask Shapes

There is also a [library of pre-built mask shapes](shapes.md) for you to use.

```pycon
>>> from word_search_generator import WordSearch
>>> from word_search_generator.mask import Star
>>> puzzle = WordSearch("dog, cat, pig", size=15)
>>> puzzle.apply_mask(Star())
>>> puzzle.show()
-----------------------------
         WORD SEARCH
-----------------------------
              K
              Y
            N C Z
            M I V
          C H X K I
D I H P X Y S J H V U C Y Q G
  V Q M V B O P F M G X F L
      H I A T I A I Y Q
        E C V G N L U
        D S A O P I J
        O R G T E Z Q
      Q G T E   A F R Z
      A C H       I Y Q
      V               W

Find these words: CAT, DOG, PIG
* Words can go S, E, SE, and, NE.

Answer Key: CAT SE @ (6, 9), DOG S @ (5, 10), PIG S @ (8, 7)
```

ℹ️ Please note, anytime a mask shape with a calculated center (Triangle, Diamond, Ellipse, Star, Heart, etc.) is applied to a puzzle with an even `size`, the mask will be offset one grid unit toward the top-left origin point (0, 0) since there is no true center of the puzzle.
