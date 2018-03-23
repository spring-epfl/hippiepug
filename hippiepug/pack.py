from enum import Enum
from warnings import warn

import msgpack

from .struct import ChainBlock, TreeNode, TreeLeaf


PROTO_VERSION = 0

CHAIN_BLOCK_MARKER = 0
TREE_NODE_MARKER = 1
TREE_LEAF_MARKER = 2
OTHER_MARKER = 3


def msgpack_encoder(obj):
    if isinstance(obj, ChainBlock):
        marker = CHAIN_BLOCK_MARKER
        obj_repr = (obj.index, obj.fingers, obj.payload)

    elif isinstance(obj, TreeNode):
        marker = TREE_NODE_MARKER
        obj_repr = (obj.pivot_key, obj.left_hash, obj.right_hash)

    elif isinstance(obj, TreeLeaf):
        marker = TREE_LEAF_MARKER
        obj_repr = (obj.lookup_key, obj.payload_hash)

    else:
        marker = OTHER_MARKER
        obj_repr = (obj,)

    return msgpack.packb((PROTO_VERSION, marker, obj_repr),
                         use_bin_type=True)


def msgpack_decoder(serialized_obj):
    proto_version, marker, obj_repr = msgpack.unpackb(
            serialized_obj,
            encoding='utf-8')
    if proto_version != PROTO_VERSION:
        warn('Serialization protocol version mismatch. '
             'Expected: %s, got: %s' % (PROTO_VERSION, proto_version))

    if marker == CHAIN_BLOCK_MARKER:
        index, fingers, payload = obj_repr
        return ChainBlock(payload=payload, index=index, fingers=fingers)

    elif marker == TREE_NODE_MARKER:
        pivot_key, left_hash, right_hash = obj_repr
        return TreeNode(pivot_key=pivot_key, left_hash=left_hash,
                        right_hash=right_hash)

    elif marker == TREE_LEAF_MARKER:
        lookup_key, payload_hash = obj_repr
        return TreeLeaf(lookup_key=lookup_key, payload_hash=payload_hash)

    else:
        return obj_repr[0]


def encode(obj, encoder=None):
    if encoder is None:
        encoder = msgpack_encoder
    return encoder(obj)


def decode(obj, decoder=None):
    if decoder is None:
        decoder = msgpack_decoder
    return decoder(obj)
