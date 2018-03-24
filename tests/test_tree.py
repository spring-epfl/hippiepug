"""
FIXME: Trees are not finished.
"""
import pytest

from mock import MagicMock

from hippiepug.tree import TreeBuilder, Tree
from hippiepug.pack import encode


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
    builder['AB']  = b'AB value'
    builder['AC']  = b'AC value'
    builder['ZZZ'] = b'ZZZ value'
    builder['Z']   = b'Z value'
    return builder.commit()


def test_builder(populated_tree):
    """Check if the tree structure is as expected."""
    tree = populated_tree
    assert tree.root_node.pivot_prefix == 'Z'

    ac_node = tree._get_node_by_hash(tree.root_node.left_hash)
    ab_leaf = tree._get_node_by_hash(ac_node.left_hash)
    ac_leaf = tree._get_node_by_hash(ac_node.right_hash)

    zz_node = tree._get_node_by_hash(tree.root_node.right_hash)
    zzz_leaf = tree._get_node_by_hash(zz_node.right_hash)
    z_leaf = tree._get_node_by_hash(zz_node.left_hash)

    assert ac_node.pivot_prefix == 'AC'
    assert ab_leaf.lookup_key == 'AB'
    assert ac_leaf.lookup_key == 'AC'

    assert zz_node.pivot_prefix == 'ZZ'
    assert zzz_leaf.lookup_key == 'ZZZ'
    assert z_leaf.lookup_key == 'Z'


def test_tree_get_by_hash_from_cache(populated_tree):
    """Check if can retrieve a node by hash from cache."""
    populated_tree._cache = MagicMock()
    populated_tree._cache.__contains__.return_value = True
    populated_tree._get_node_by_hash(populated_tree.root)
    populated_tree._cache.__getitem__.assert_called_with(
            populated_tree.root)


def test_tree_get_by_hash_from_store(populated_tree):
    """Check if can retrieve a node by hash from store."""
    expected_node = populated_tree._get_node_by_hash(populated_tree.root)
    assert expected_node.pivot_prefix == 'Z'


def test_tree_inclusion_proof(populated_tree):
    """Check tree (non-)inclusion proof."""

    # Inclusion in the right subtree.
    _, (path, closure) = populated_tree.get_value_by_lookup_key(
            'Z', return_proof=True)
    assert len(path) == 3
    assert path[0].pivot_prefix == 'Z'
    assert path[1].pivot_prefix == 'ZZ'
    assert path[2].lookup_key == 'Z'

    assert len(closure) == 2
    assert closure[0].pivot_prefix == 'AC'
    assert closure[1].lookup_key == 'ZZZ'

    # Inclusion in the left subtree.
    path, closure = populated_tree.get_inclusion_proof('AC')
    assert len(path) == 3
    assert path[0].pivot_prefix == 'Z'
    assert path[1].pivot_prefix == 'AC'
    assert path[2].lookup_key == 'AC'

    assert len(closure) == 2
    assert closure[0].pivot_prefix == 'ZZ'
    assert closure[1].lookup_key == 'AB'

    # Non-inclusion.
    path, closure = populated_tree.get_inclusion_proof('ZZ')
    assert len(path) == 3
    assert path[0].pivot_prefix == 'Z'
    assert path[1].pivot_prefix == 'ZZ'
    assert path[2].lookup_key == 'ZZZ'

    assert len(closure) == 2
    assert closure[0].pivot_prefix == 'AC'
    assert closure[1].lookup_key == 'Z'


def test_tree_contains(populated_tree):
    """Check membership query."""
    assert 'AB' in populated_tree
    assert 'AC' in populated_tree
    assert 'ZZZ' in populated_tree
    assert 'Z' in populated_tree
    assert 'ZZ' not in populated_tree


def test_tree_get_by_lookup_key(populated_tree):
    """Check lookup key queries."""
    assert populated_tree['AB'] == b'AB value'
    assert populated_tree['AC'] == b'AC value'
    assert populated_tree['ZZZ'] == b'ZZZ value'
    assert populated_tree['Z'] == b'Z value'
    with pytest.raises(KeyError):
        value = populated_tree['ZZ']


def test_tree_get_node_by_hash_fails_if_not_node(populated_tree):
    """Check that exception is raised if the object is not a node."""
    extra_obj_hash = populated_tree.object_store.add(encode(b'extra'))
    with pytest.raises(ValueError):
        populated_tree._get_node_by_hash(extra_obj_hash)
