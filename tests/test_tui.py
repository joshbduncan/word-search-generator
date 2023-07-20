# import pytest

from word_search_generator import WordSearch
from word_search_generator.tui.word_search import TUIGame


def test_tui_title():
    ws = WordSearch()
    ws.random_words(10)
    app = TUIGame(ws)
    assert app.title == "TUIGame"


# @pytest.mark.asyncio
# async def test_tui_elements():
#     ws = WordSearch()
#     ws.random_words(10)
#     app = TUIGame(ws)
#     async with app.run_test() as pilot:
#         await pilot.click()
#         assert False
