import pytest

from hippiepug.store import Sha256DictStore


@pytest.fixture
def object_store():
    return Sha256DictStore()

