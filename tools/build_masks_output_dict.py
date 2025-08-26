import io
from contextlib import redirect_stdout

from word_search_generator.mask import Mask
from word_search_generator.mask.shapes import BUILTIN_MASK_SHAPES

MASKS: dict[str, str] = {}


preview_size: int = 21
for name, shape in BUILTIN_MASK_SHAPES.items():
    mask: Mask = shape()
    mask.generate(preview_size)

    with io.StringIO() as buf, redirect_stdout(buf):
        mask.show()
        output: str = buf.getvalue()

    MASKS[name] = output

print(MASKS)
