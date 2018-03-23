"""
FIXME: Trees are not finished.
"""
import pytest

from hippiepug.tree import TreeMapBuilder


# def test_node_serialization():
#     node._payload_hash = b'yada'
#     deserialized_node = node.__class__.deserialize(node.serialize())
#     assert deserialized_node.payload_hash == node.payload_hash


def test_tree_builder(object_store):
    builder = TreeMapBuilder(object_store)
    builder['A']     = b'A object'
    builder['AA']    = b'A object'
    builder['AB']    = b'B object'
    builder['ZZ']    = b'C object'
    builder['ZZZ']   = b'C object'
    builder['ZZZAA'] = b'C object'
    builder.commit()
