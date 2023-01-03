import timeit

setup = """\
from word_search_generator import WordSearch
from word_search_generator.mask.shapes import Star
from word_search_generator.utils import get_random_words
"""

stmt = """\
p=WordSearch(size=50)
p.apply_mask(Star())
p.add_words(",".join(get_random_words(100)))"""

result = timeit.timeit(stmt=stmt, setup=setup, number=10)
print(result)

"""
RESULTS:

V1 = 12.544383415000993
V2 = 16.73762503299986
V3 = 35.81765231499958
"""
