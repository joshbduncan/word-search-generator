from word_search_generator.mask.ellipse import Ellipse


def test_calculate_ellipse_points_method_1():
    """Even `puzzle_size`, odd `width` and `height`."""
    puzzle_size = 6
    points = Ellipse.calculate_ellipse_points(
        width=5,
        height=3,
        origin=(puzzle_size // 2, puzzle_size // 2),
        puzzle_size=puzzle_size,
    )
    assert len(points) % 2 == 1


def test_calculate_ellipse_points_method_2():
    """Odd `puzzle_size`, even `width` and `height`."""
    puzzle_size = 7
    points = Ellipse.calculate_ellipse_points(
        width=6,
        height=4,
        origin=(puzzle_size // 2, puzzle_size // 2),
        puzzle_size=puzzle_size,
    )
    assert len(points) % 2 == 0


def test_within_radius_true():
    width = 10
    height = 6
    width_r = width / 2
    height_r = height / 2
    ratio = width_r / height_r
    assert Ellipse.within_radius(1, 2, width_r, ratio)


def test_within_radius_false():
    width = 4
    height = 2
    width_r = width / 2
    height_r = height / 2
    ratio = width_r / height_r
    assert not Ellipse.within_radius(7, 11, width_r, ratio)
