import tempfile

import pytest


@pytest.fixture(scope="session")
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
