"""
FIXME: Trees are not finished.
"""

from hippiepug.tree import MsgpackNode, TreeMapBuilder


def test_tree_builder(object_store):
    builder = TreeMapBuilder(MsgpackNode, object_store)
    builder['A key'] = b'A object'
    builder['B key'] = b'A object'
    builder.commit()

