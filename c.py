class Mask:
    def __init__(self, points=[]) -> None:
        self.points = points
        self.mask = []

    def generate(self, puzzle_size) -> None:
        self.points.append(f"MASK-{puzzle_size}")

    def show(self) -> None:
        print(f"{self.points=}")


class Circle(Mask):
    def __init__(self, points=[]) -> None:
        super().__init__(points=points)

    def generate(self, puzzle_size) -> None:
        self.points.append(f"CIRCLE-{puzzle_size}")


class Star(Mask):
    def __init__(self, points=[]) -> None:
        super().__init__(points=points)

    def generate(self, puzzle_size) -> None:
        self.points.append(f"STAR-{puzzle_size}")


class CompoundMask:
    def __init__(self, points=[]) -> None:
        self.points = points
        self.masks = []

    def add_mask(self, mask: Mask) -> None:
        self.masks.append(mask)

    def generate(self, puzzle_size) -> None:
        for mask in self.masks:
            print(f"generating mask {mask}")
            mask.generate(puzzle_size)
            self.points.append(mask.points)
