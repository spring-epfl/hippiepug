"""
Serializers for chain blocks and tree nodes.

.. warning::
    You need to take extra care when defining custom serializations. Be
    sure that your serialization includes all the fields in the original
    structure. E.g., for chain blocks:

    - ``self.index``
    - ``self.fingers``
    - Your payload

    Unless this is done, the integrity of the data structures is screwed, since
    it's the serialized versions of nodes and blocks that are hashed.
"""

from warnings import warn

from defaultcontext import with_default_context

import attr
import msgpack

from .struct import ChainBlock, TreeNode, TreeLeaf


PROTO_VERSION = 0

CHAIN_BLOCK_MARKER = 0
TREE_NODE_MARKER = 1
TREE_LEAF_MARKER = 2
OTHER_MARKER = 3


def msgpack_encoder(obj):
    """Represent structure as tuple and serialize using msgpack.

    Default encoder.
    """

    if isinstance(obj, ChainBlock):
        marker = CHAIN_BLOCK_MARKER
        obj_repr = (obj.index, obj.fingers, obj.payload)

    elif isinstance(obj, TreeNode):
        marker = TREE_NODE_MARKER
        obj_repr = (obj.pivot_prefix, obj.left_hash, obj.right_hash)

    elif isinstance(obj, TreeLeaf):
        marker = TREE_LEAF_MARKER
        obj_repr = (obj.lookup_key, obj.payload_hash)

    else:
        marker = OTHER_MARKER
        obj_repr = (obj,)

    return msgpack.packb((PROTO_VERSION, marker, obj_repr),
                         use_bin_type=True)


def msgpack_decoder(serialized_obj):
    """Deserialize structure from msgpack-encoded tuple.

    Default decoder.
    """

    try:
        proto_version, marker, obj_repr = msgpack.unpackb(
                serialized_obj,
                encoding='utf-8')
    except Exception as e:
        raise ValueError('Object could not be decoded: %s' % e)

    if proto_version != PROTO_VERSION:
        warn('Serialization protocol version mismatch. '
             'Expected: %s, got: %s' % (PROTO_VERSION, proto_version))

    if marker == CHAIN_BLOCK_MARKER:
        index, fingers, payload = obj_repr
        return ChainBlock(payload=payload, index=index, fingers=fingers)

    elif marker == TREE_NODE_MARKER:
        pivot_prefix, left_hash, right_hash = obj_repr
        return TreeNode(pivot_prefix=pivot_prefix, left_hash=left_hash,
                        right_hash=right_hash)

    elif marker == TREE_LEAF_MARKER:
        lookup_key, payload_hash = obj_repr
        return TreeLeaf(lookup_key=lookup_key, payload_hash=payload_hash)

    else:
        return obj_repr[0]


@with_default_context(use_empty_init=True)
@attr.s
class EncodingParams(object):
    """Thread-local container for default encoder and decoder funcs.

    :param encoder: Default encoder
    :param decoder: Default decoder

    This is how you can override the defaults using this class:

    >>> my_params = EncodingParams()
    >>> my_params.encoder = lambda obj: b'encoded!'
    >>> my_params.decoder = lambda encoded: b'decoded!'
    >>> EncodingParams.set_global_default(my_params)
    >>> encode(b'dummy') == b'encoded!'
    True
    >>> decode(b'encoded!') == b'decoded!'
    True
    >>> EncodingParams.reset_defaults()
    """
    encoder = attr.ib(default=attr.Factory(lambda: msgpack_encoder))
    decoder = attr.ib(default=attr.Factory(lambda: msgpack_decoder))


def encode(obj, encoder=None):
    """Serialize object.

    :param obj: Chain block, tree node, or bytes
    :param encoder: Custom serializer
    """

    if encoder is None:
        encoder = EncodingParams.get_default().encoder
    return encoder(obj)


def decode(serialized, decoder=None):
    """Deserialize object.

    :param serialized: Encoded structure
    :param encoder: Custom de-serializer
    """

    if decoder is None:
        decoder = EncodingParams.get_default().decoder
    return decoder(serialized)
