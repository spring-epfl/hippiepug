import pytest

from hippiepug.pack import encode, decode
from hippiepug.pack import EncodingParams


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


def test_custom_defaults():
    def mock_encoder(obj):
        return b'encoded!'

    def mock_decoder(obj):
        return b'decoded!'

    mock_params = EncodingParams()
    mock_params.encoder = mock_encoder
    mock_params.decoder = mock_decoder

    with mock_params.as_default():
        obj = b'dummy'
        assert encode(obj) == b'encoded!'
        assert decode(obj) == b'decoded!'


@pytest.mark.parametrize('thing', [42, b'giberrish', (1, 2, b'obj')])
def test_decode_raises_when_format_unknown(thing):
    """Check the decode raises when serialization format not understood."""
    with pytest.raises(ValueError):
        decode(thing)

