import word_search_generator

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="word-search-generator",
    version=getattr(word_search_generator, "__version__"),
    author="Josh Duncan",
    author_email="joshbduncan@gmail.com",
    description="Make awesome Word Search puzzles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshbduncan/word-search-generator",
    project_urls={
        "Bug Tracker": "https://github.com/joshbduncan/word-search-generator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    keywords=["puzzles", "words", "games"],
    packages=find_packages(include=["word_search_generator"]),
    install_requires=["fpdf2"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "word-search=word_search_generator.__main__:cli",
        ],
    },
)
