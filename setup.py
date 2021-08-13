from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="word-search-generator",
    version="1.0.0",
    author="Josh Duncan",
    author_email="joshbduncan@gmail.com",
    description="Make awesome Word Search puzzles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/joshbduncan/word-search",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
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
