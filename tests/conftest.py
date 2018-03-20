import pytest

from hippiepug.store import DictStore


@pytest.fixture
def object_store():
    return DictStore()

