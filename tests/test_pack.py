import pytest

from hippiepug.pack import encode, decode


@pytest.mark.parametrize('obj', [
    pytest.lazy_fixture('node'),
    pytest.lazy_fixture('leaf'),
    pytest.lazy_fixture('block'),
    b'binary string'
])
def test_msgpack_serialization(obj):
    """Check serialization correctness."""
    a = obj
    serialized = encode(a)
    b = decode(serialized)
    assert a == b
