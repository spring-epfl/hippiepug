"""
FIXME: Trees are not finished.
"""
import pytest

from mock import MagicMock

from hippiepug.tree import TreeBuilder, Tree
from hippiepug.tree import verify_tree_inclusion_proof
from hippiepug.pack import encode


LOOKUP_KEYS = ['AB', 'AC', 'ZZZ', 'Z']

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
    for lookup_key in LOOKUP_KEYS:
        builder[lookup_key] = b'{} value'.format(lookup_key.encode('utf-8'))
    return builder.commit()


def test_builder_fails_when_no_items(object_store):
    tree_builder = TreeBuilder(object_store)
    with pytest.raises(ValueError):
        tree_builder.commit()

    tree_builder['a'] = b'b'
    tree_builder.commit()


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


def test_tree_inclusion_proof(populated_tree):
    """Manually check tree (non-)inclusion proof."""

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
    _, (path, closure) = populated_tree.get_value_by_lookup_key('AC',
            return_proof=True)
    assert len(path) == 3
    assert path[0].pivot_prefix == 'Z'
    assert path[1].pivot_prefix == 'AC'
    assert path[2].lookup_key == 'AC'

    assert len(closure) == 2
    assert closure[0].pivot_prefix == 'ZZ'
    assert closure[1].lookup_key == 'AB'

    # Non-inclusion.
    _, (path, closure) = populated_tree.get_value_by_lookup_key('ZZ',
            return_proof=True)
    assert len(path) == 3
    assert path[0].pivot_prefix == 'Z'
    assert path[1].pivot_prefix == 'ZZ'
    assert path[2].lookup_key == 'ZZZ'

    assert len(closure) == 2
    assert closure[0].pivot_prefix == 'AC'
    assert closure[1].lookup_key == 'Z'


@pytest.mark.parametrize('lookup_key', LOOKUP_KEYS)
def test_tree_proof_verif(populated_tree, lookup_key):
    """Check proof of inclusion verification."""
    root = populated_tree.root
    payload, proof = populated_tree.get_value_by_lookup_key(lookup_key,
            return_proof=True)
    store = populated_tree.object_store.__class__()
    assert verify_tree_inclusion_proof(
            store, root, lookup_key, payload, proof)


@pytest.mark.parametrize('lookup_key', LOOKUP_KEYS)
def test_tree_proof_verif_fails_when_leaf_different(
        populated_tree, lookup_key):
    """Check proof fails when lookup_key in the leaf is different."""
    root = populated_tree.root
    payload, proof = populated_tree.get_value_by_lookup_key(lookup_key,
            return_proof=True)
    store = populated_tree.object_store.__class__()
    proof[0][-1].lookup_key = 'hacked'

    assert not verify_tree_inclusion_proof(
            store, root, lookup_key, payload, proof)


@pytest.mark.parametrize('lookup_key', LOOKUP_KEYS)
def test_tree_proof_verif_fails_when_payload_different(
        populated_tree, lookup_key):
    """Check proof of inclusion fails when payload is different."""
    root = populated_tree.root
    store = populated_tree.object_store.__class__()
    payload, proof = populated_tree.get_value_by_lookup_key(lookup_key,
            return_proof=True)
    payload = b'non-existent'

    assert not verify_tree_inclusion_proof(
            store, root, lookup_key, payload, proof)


@pytest.mark.parametrize('lookup_key', LOOKUP_KEYS)
def test_tree_proof_verif_fails_when_lacks_closure(
        populated_tree, lookup_key):
    """Check proof of inclusion fails when it lacks closure."""
    root = populated_tree.root
    payload, proof = populated_tree.get_value_by_lookup_key(lookup_key,
            return_proof=True)
    store = populated_tree.object_store.__class__()
    path, closure = proof
    bad_proof = (path, [])

    with pytest.warns(UserWarning, match='Not enough nodes'):
        assert not verify_tree_inclusion_proof(
                store, root, lookup_key, payload, bad_proof)


@pytest.mark.parametrize('lookup_key', LOOKUP_KEYS)
def test_tree_proof_verif_fails_when_path_is_bad(
        populated_tree, lookup_key):
    """Check proof of inclusion fails when path is bad."""
    root = populated_tree.root
    store = populated_tree.object_store.__class__()
    payload, proof = populated_tree.get_value_by_lookup_key(lookup_key,
            return_proof=True)
    path, closure = proof
    bad_proof = (path[:2], closure)

    assert not verify_tree_inclusion_proof(
            store, root, lookup_key, payload, bad_proof)
