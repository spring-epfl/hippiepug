"""
FIXME: Trees are not finished.
"""

import abc
import collections
import os

from .store import Sha256DictStore
from .node import TreeNode, TreeLeaf
from .pack import encode, decode


class Tree(object):
    """
    View of a committed Merkle tree.

    :param object_store: Object store
    :param head: The hash of the head block
    :param cache: Cache
    :type cache: dict
    """

    def __init__(self, object_store, head,
                 cache=None):

        self.object_store = object_store
        self.head = head
        self.cache = cache or {}

    def get_node_by_hash(self, node_hash):
        if node_hash in self.cache:
            return self.cache[node_hash]

        serialized_node = self.object_store.get(
                node_hash, check_integrity=True)
        if serialized_node is not None:
            node = decode(serialized_node)
            self.cache[node_hash] = block
            return node

    def get_inclusion_evidence(self, lookup_key):
        return None

    def __contains__(self, item):
        evidence = self.get_inclusion_evidence(item)
        return len(evidence) > 0

    def __getitem__(self, item):
        evidence = self.get_inclusion_evidence(item)

    @property
    def head_node(self):
        """
        Get the head node.
        """
        return self.object_store.get(self.head)


class TreeMapBuilder(object):
    """Builder for a Merkle tree-based verifiable map.

    :param object_store: Object store

    .. warning::
       All read accesses are cached. The cache is assumed to be trusted,
       so blocks retrieved from cache are not checked for integrity, unlike
       when they are retrieved from the object store.

    .. seealso::
       * :py:class:`hippiehug.tree.Tree`
       * :py:class:`hippiepug.chain.Chain`
    """

    def __init__(self, object_store=None):
        if object_store is None:
            object_store = Sha256DictStore()
        self.object_store = object_store
        self.items = {}

    def __setitem__(self, k, v):
        self.items[k] = v

    def __getitem__(self, k):
        return self.items(k)

    def _make_subtree(self, items):
        """Build a tree from sorted items."""
        if len(items) == 0:
            raise ValueError("No items to put.")
        if len(items) == 1:
            (key, serialized_obj), = items
            value_hash = self.object_store.hash_object(serialized_obj)
            leaf = TreeLeaf(lookup_key=key, payload_hash=value_hash)
            return [leaf]

        else:
            middle = len(items) // 2
            pivot_key, pivot_obj = items[middle]
            left_partition = items[:middle]
            right_partition = items[middle:]
            left_subtree_nodes = self._make_subtree(left_partition)
            right_subtree_nodes = self._make_subtree(right_partition)

            # Compute minimal lookup prefixes
            pivot_keys = [pivot_key]
            left_child = left_subtree_nodes[0]
            right_child = right_subtree_nodes[0]

            def get_node_key(node):
                if isinstance(node, TreeLeaf):
                    return node.lookup_key
                elif isinstance(node, TreeNode):
                    return node.pivot_key

            if left_subtree_nodes:
                pivot_keys.append(get_node_key(left_child))
            if right_subtree_nodes:
                pivot_keys.append(get_node_key(right_child))
            common_prefix = os.path.commonprefix(pivot_keys)
            pivot_key = pivot_key[:max(1, len(common_prefix))]

            # Compute hashes of direct children.
            left_hash = None
            right_hash = None
            left_hash=self.object_store.hash_object(
                encode(left_subtree_nodes[0]))
            right_hash=self.object_store.hash_object(
                encode(right_subtree_nodes[0]))

            pivot_node = TreeNode(pivot_key=pivot_key,
                    left_hash=left_hash, right_hash=right_hash)

            return [pivot_node] + left_subtree_nodes + right_subtree_nodes

    def commit(self):
        """
        Commit items to the tree.

        :param items: An iterable of comparable and serializable items
        :type items: Byte string is best
        """
        items = sorted(self.items.items(), key=lambda t: t[0])
        nodes = self._make_subtree(items)

        # Put intermediate nodes into the store.
        for node in nodes:
            serialized_node = encode(node)
            self.object_store.add(serialized_node)

        # Put items themselves into the store.
        for serialized_obj in self.items.values():
            self.object_store.add(serialized_obj)

        head_node = nodes[0]
        head = self.object_store.hash_object(encode(head_node))

