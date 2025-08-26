__all__ = [
    "Mask",
    "CompoundMask",
    "Bitmap",
    "ImageMask",
    "Ellipse",
    "Polygon",
    "Rectangle",
    "RegularPolygon",
    "Star",
]

# Import all base masks shapes for easier access
# (eg. `mask.Star` vs. `mask.polygon.Star`)
from .bitmap import Bitmap as Bitmap
from .bitmap import ImageMask as ImageMask
from .ellipse import Ellipse as Ellipse
from .mask import CompoundMask, Mask
from .polygon import Polygon as Polygon
from .polygon import Rectangle as Rectangle
from .polygon import RegularPolygon as RegularPolygon
from .polygon import Star as Star
