"""
FIXME: Trees are not finished.
"""
import pytest

from mock import MagicMock

from hippiepug.struct import TreeNode, TreeLeaf
from hippiepug.tree import TreeBuilder
from hippiepug.pack import encode, decode

# Test tree:
#     /ZZZ-|
#   ZZ
#  /  \Z---|
# Z   /AC--|
#  \AC
#     \AB--|
@pytest.fixture
def populated_tree(object_store):
    builder = TreeBuilder(object_store)
    builder['AB']  = b'dummy'
    builder['AC']  = b'dummy'
    builder['ZZZ'] = b'dummy'
    builder['Z']   = b'dummy'
    return builder.commit()


def test_builder(populated_tree):
    """Check if the tree structure is as expected."""
    tree = populated_tree
    assert tree.root_node.pivot_key == 'Z'

    ac_node = tree.get_node_by_hash(tree.root_node.left_hash)
    ab_leaf = tree.get_node_by_hash(ac_node.left_hash)
    ac_leaf = tree.get_node_by_hash(ac_node.right_hash)

    zz_node = tree.get_node_by_hash(tree.root_node.right_hash)
    zzz_leaf = tree.get_node_by_hash(zz_node.right_hash)
    z_leaf = tree.get_node_by_hash(zz_node.left_hash)

    assert ac_node.pivot_key == 'AC'
    assert ab_leaf.lookup_key == 'AB'
    assert ac_leaf.lookup_key == 'AC'

    assert zz_node.pivot_key == 'ZZ'
    assert zzz_leaf.lookup_key == 'ZZZ'
    assert z_leaf.lookup_key == 'Z'


def test_tree_query_by_hash_from_cache(populated_tree):
    """Check if can retrieve a node by hash from cache."""
    populated_tree._cache = MagicMock()
    populated_tree._cache.__contains__.return_value = True
    populated_tree.get_node_by_hash(populated_tree.root)
    populated_tree._cache.__getitem__.assert_called_with(
            populated_tree.root)


def test_tree_query_by_hash_from_store(populated_tree):
    """Check if can retrieve a node by hash from store."""
    expected_node = populated_tree.get_node_by_hash(populated_tree.root)
    assert expected_node.pivot_key == 'Z'


def test_tree_inclusion_evidence(populated_tree):
    """Check tree (non-)inclusion evidence."""

    # Inclusion in the right subtree.
    path, closure = populated_tree.get_inclusion_evidence('Z')
    assert len(path) == 3
    assert path[0].pivot_key == 'Z'
    assert path[1].pivot_key == 'ZZ'
    assert path[2].lookup_key == 'Z'

    assert len(closure) == 2
    assert closure[0].pivot_key == 'AC'
    assert closure[1].lookup_key == 'ZZZ'

    # Inclusion in the left subtree.
    path, closure = populated_tree.get_inclusion_evidence('AC')
    assert len(path) == 3
    assert path[0].pivot_key == 'Z'
    assert path[1].pivot_key == 'AC'
    assert path[2].lookup_key == 'AC'

    assert len(closure) == 2
    assert closure[0].pivot_key == 'ZZ'
    assert closure[1].lookup_key == 'AB'

    # Non-inclusion.
    path, closure = populated_tree.get_inclusion_evidence('ZZ')
    assert len(path) == 3
    assert path[0].pivot_key == 'Z'
    assert path[1].pivot_key == 'ZZ'
    assert path[2].lookup_key == 'ZZZ'

    assert len(closure) == 2
    assert closure[0].pivot_key == 'AC'
    assert closure[1].lookup_key == 'Z'


def test_tree_contains(populated_tree):
    """Check membership query."""
    assert 'AB' in populated_tree
    assert 'AC' in populated_tree
    assert 'ZZZ' in populated_tree
    assert 'Z' in populated_tree
    assert 'ZZ' not in populated_tree
