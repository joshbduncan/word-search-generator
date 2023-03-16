import io
from contextlib import redirect_stdout

from word_search_generator.mask import shapes

MASKS = {}


preview_size = 21
for shape in shapes.BUILTIN_MASK_SHAPES:
    mask = eval(f"shapes.{shape}")()
    mask.generate(preview_size)

    with io.StringIO() as buf, redirect_stdout(buf):
        mask.show()
        output = buf.getvalue()

    MASKS[shape] = output

print(MASKS)
