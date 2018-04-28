"""
Tools for building and interpreting key-value Merkle trees.
"""

import os

from warnings import warn

from .struct import TreeNode, TreeLeaf
from .store import IntegrityValidationError
from .pack import encode, decode


def _is_leaf(node):
    """Check if a node is a leaf node."""
    return isinstance(node, TreeLeaf)


def _is_inner_node(node):
    """Check if a node is an inner tree node."""
    return isinstance(node, TreeNode)


class Tree(object):
    """
    View of a Merkle tree.

    Use :py:class:`TreeBuilder` to build a Merkle tree first.

    :param object_store: Object store
    :param root: The hash of the root node
    :param cache: Cache
    :type cache: dict

    .. warning::
       All read accesses are cached. The cache is assumed to be trusted,
       so blocks retrieved from cache are not checked for integrity, unlike
       when they are retrieved from the object store.

    .. seealso::
       * :py:class:`hippiepug.chain.Chain`
    """

    def __init__(self, object_store, root, cache=None):
        self.object_store = object_store
        self.root = root
        self._cache = cache or {}

    def _get_node_by_hash(self, node_hash):
        """Unsafely retrieve node by its hash.

        After retrieving, decodes the node.

        .. warning::
            This function does not check if the retrieved node
            belongs to this chain.

        :raises: ``TypeError`` if retrieved object is not
                 a tree node.
        """
        # Get the node from cache if it is in the cache.
        if node_hash in self._cache:
            return self._cache[node_hash]

        serialized_node = self.object_store.get(
                node_hash, check_integrity=True)
        if serialized_node is not None:
            node = decode(serialized_node)
            if not _is_leaf(node) and not _is_inner_node(node):
                raise TypeError('Object with this hash is not a tree node.')
            self._cache[node_hash] = node
            return node

    def _get_inclusion_proof(self, lookup_key):
        """Get (non-)inclusion proof for a lookup key.

        :param lookup_key: Lookup key
        :returns: A tuple with a path to a leaf node, and a list of other
                  nodes needed to reproduce the tree root.
        """
        # Nodes on the path from the root to the leaf.
        path_nodes = []
        current_node = self.root_node
        while True:
            path_nodes.append(current_node)
            left_child = right_child = None
            try:
                # If current node is an intermediate node, get its left or
                # right child according to the pivot value.
                if _is_inner_node(current_node):
                    if lookup_key < current_node.pivot_prefix:
                        current_node = self._get_node_by_hash(
                                current_node.left_hash)
                    else:
                        current_node = self._get_node_by_hash(
                                current_node.right_hash)

                    # If a child is not found, cannot continue the lookup.
                    if current_node is None:
                        raise ValueError('A required node was not found')

                # Stop when the current node is a leaf.
                elif _is_leaf(current_node):
                    break

                # Not a tree node. Likely a malformed object.
                else:
                    raise TypeError('Invalid node type.')

            # Warn that the lookup failed, and return whatever was found
            # on the path.
            except Exception as e:
                warn('Exception occured when handling node %s: %s' % (
                    current_node, e))
                break

        return path_nodes

    def get_value_by_lookup_key(self, lookup_key, return_proof=False):
        """Retrieve value by its lookup key.

        :param lookup_key: Lookup key
        :param return_proof: Whether to return inclusion proof
        :returns: Only the value when ``return_proof`` is False, and a
                  ``(value, proof)`` tuple when ``return_proof`` is True.
                  A value is ``None`` when the lookup key was not found.
        """
        path = self._get_inclusion_proof(lookup_key)
        result = None
        if path and path[-1] is not None:
            # Check whether the last node in the path is a leaf, and its
            # lookup key is what we were looking for.
            if _is_leaf(path[-1]) and (path[-1].lookup_key == lookup_key):
                result = self.object_store.get(path[-1].payload_hash)

        if return_proof:
            return result, path
        else:
            return result

    def __contains__(self, lookup_key):
        """Check if lookup key is in the tree."""
        try:
            self.__getitem__(lookup_key)
            return True
        except KeyError:
            return False

    def __getitem__(self, lookup_key):
        """Retrieve value by its lookup key.

        :returns: Corresponding value
        :raises: ``KeyError`` when the lookup key was not found.
        """
        value = self.get_value_by_lookup_key(lookup_key, return_proof=False)
        if value is None:
            raise KeyError('The item with given lookup key was not found.')
        else:
            return value

    @property
    def root_node(self):
        """The root node."""
        return self._get_node_by_hash(self.root)

    def __repr__(self):
        return ('Tree('  # pragma: no cover
                'object_store={self.object_store}, '
                'root=\'{self.root}\')').format(
                    self=self)


class TreeBuilder(object):
    """Builder for a key-value Merkle tree.

    :param object_store: Object store

    You can add items using a dict-like interface:

    >>> from .store import Sha256DictStore
    >>> store = Sha256DictStore()
    >>> builder = TreeBuilder(store)
    >>> builder['foo'] = b'bar'
    >>> builder['baz'] = b'zez'
    >>> tree = builder.commit()
    >>> 'foo' in tree
    True
    """

    def __init__(self, object_store):
        self.object_store = object_store
        self.items = {}

    def __setitem__(self, lookup_key, value):
        """Add item for committing to the tree."""
        self.items[lookup_key] = value

    def _make_subtree(self, items):
        """Build a tree from sorted items.

        :param items: An iterable of comparable and serializable items
        """
        if len(items) == 0:
            raise ValueError("No items to put.")

        if len(items) == 1:
            (key, serialized_obj), = items
            value_hash = self.object_store.hash_object(serialized_obj)
            leaf = TreeLeaf(lookup_key=key, payload_hash=value_hash)
            return [leaf]

        else:
            middle = len(items) // 2
            pivot_prefix, pivot_obj = items[middle]
            left_partition = items[:middle]
            # NOTE: The right partition includes the pivot node
            right_partition = items[middle:]
            left_subtree_nodes = self._make_subtree(left_partition)
            right_subtree_nodes = self._make_subtree(right_partition)

            # Compute minimal lookup prefixes
            pivot_prefixes = [pivot_prefix]
            left_child = left_subtree_nodes[0]
            right_child = right_subtree_nodes[0]

            def get_node_key(node):
                if _is_leaf(node):
                    return node.lookup_key
                elif _is_inner_node(node):
                    return node.pivot_prefix

            if left_subtree_nodes:
                pivot_prefixes.append(get_node_key(left_child))
            if right_subtree_nodes:
                pivot_prefixes.append(get_node_key(right_child))
            common_prefix = os.path.commonprefix(pivot_prefixes)
            pivot_prefix = pivot_prefix[:max(1, len(common_prefix) + 1)]

            # Compute hashes of direct children.
            left_hash = None
            right_hash = None
            left_hash = self.object_store.hash_object(
                encode(left_subtree_nodes[0]))
            right_hash = self.object_store.hash_object(
                encode(right_subtree_nodes[0]))

            pivot_node = TreeNode(pivot_prefix=pivot_prefix,
                    left_hash=left_hash, right_hash=right_hash)

            return [pivot_node] + left_subtree_nodes + right_subtree_nodes

    # TODO: Figure out if we can have this as an atomic transaction
    def commit(self):
        """Commit items to the tree."""
        items = sorted(self.items.items(), key=lambda t: t[0])
        nodes = self._make_subtree(items)

        # Put intermediate nodes into the store.
        for node in nodes:
            serialized_node = encode(node)
            self.object_store.add(serialized_node)

        # Put items themselves into the store.
        for serialized_obj in self.items.values():
            self.object_store.add(serialized_obj)

        root_node = nodes[0]
        root = self.object_store.hash_object(encode(root_node))
        return Tree(self.object_store, root)

    def __repr__(self):
        return ('TreeBuilder('  # pragma: no cover
                'object_store={self.object_store}, '
                'items={self.items})').format(
                    self=self)


def verify_tree_inclusion_proof(store, root, lookup_key, value, proof):
    """Verify inclusion proof for a tree.

    :param store: Object store, may be empty
    :param head: Tree root
    :param lookup_key: Lookup key
    :param value: Value associated with the lookup key
    :param proof: Inclusion proof
    :type proof: tuple containing list of decoded path nodes
    :returns: bool
    """
    for node in proof:
        store.add(encode(node))
    store.add(value)
    verifier_tree = Tree(store, root=root)
    retrieved_payload = verifier_tree.get_value_by_lookup_key(lookup_key)
    return retrieved_payload == value

