"""
FIXME: Trees are not finished.
"""
import pytest

from hippiepug.struct import TreeNode, TreeLeaf
from hippiepug.tree import TreeMapBuilder
from hippiepug.pack import encode, decode


def test_tree_builder(object_store):
    builder = TreeMapBuilder(object_store)
    builder['A']     = b'A object'
    builder['AA']    = b'A object'
    builder['AB']    = b'B object'
    builder['ZZ']    = b'C object'
    builder['ZZZ']   = b'C object'
    builder['ZZZAA'] = b'C object'
    builder.commit()
