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

@pytest.mark.parametrize('thing', [42, b'giberrish', (1, 2, b'obj')])
def test_decode_raises_when_format_unknown(thing):
    """Check the decode raises when serialization format not understood."""
    with pytest.raises(ValueError):
        decode(thing)

