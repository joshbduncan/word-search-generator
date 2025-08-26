from importlib.resources import files
from pathlib import PurePath

data_dir = files("word_search_generator").joinpath("data")

WORD_LISTS: dict[str, list[str]] = {}


for entry in data_dir.iterdir():
    if entry.is_file() and entry.name.endswith(".txt"):
        stem = PurePath(entry.name).stem
        WORD_LISTS[stem] = entry.read_text(encoding="utf-8").splitlines()
