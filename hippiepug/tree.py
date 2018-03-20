"""
FIXME: Trees are not finished.
"""

import abc
import collections
import msgpack

from .utils import Serializable
from .store import DictStore


class BaseNode(Serializable):
    """Merkle tree node.

    :param lookup_prefix:
    :param payload:
    :param left_hash:
    :param right_hash:
    """

    def __init__(self, lookup_prefix=None, payload_hash=None, left_hash=None, right_hash=None):
        self._lookup_prefix = lookup_prefix
        self._payload_hash = payload_hash
        self._left_hash = left_hash
        self._right_hash = right_hash

    @property
    def lookup_prefix(self):
        return self._lookup_prefix

    @property
    def payload_hash(self):
        return self._payload_hash

    @property
    def left_hash(self):
        return self._left_hash

    @property
    def right_hash(self):
        return self._right_hash

    @property
    def is_leaf(self):
        return self.left_hid is None and self.right_hid is None


class MsgpackNode(BaseNode):

    def serialize(self):
        """Serialize node, in particular for hashing."""
        return msgpack.packb(
                (self.lookup_prefix, self.payload_hash,
                    self.left_hash, self.right_hash),
                use_bin_type=True)

    def deserialize(cls, serialized_node):
        """Deserialize node."""
        unpacked = msgpack.unpackb(serialized_node, raw=False)
        lookup_prefix, payload_hash, left_hash, right_hash = unpacked
        return cls(lookup_prefix, payload_hash, left_hash, right_hash)


class Tree(object):
    """
    View of a committed Merkle tree

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
            node = Node.deserialize(serialized_node)
            self.cache[node_hash] = block
        return raw_node.deserialize()

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

    def __init__(self, node_cls, object_store=None):
        self.node_cls = node_cls
        if object_store is None:
            object_store = DictStore()
        self.object_store = object_store
        self.items = {}

    def __setitem__(self, k, v):
        self.items[k] = v

    def __getitem__(self, k):
        return self.items(k)

    def _make_subtree(self, items):
        """Build a tree from sorted items."""
        if len(items) == 0:
            return None, []
        if len(items) == 1:
            (key, serialized_obj), = items
            value_hash = self.object_store.hash_object(serialized_obj)
            leaf = self.node_cls(lookup_prefix=key, payload_hash=value_hash)
            return leaf, []
        else:
            middle = len(items) // 2
            pivot_key, pivot_obj = items[middle]
            left_partition = items[:middle]
            right_partition = items[middle+1:]
            left_child, left_subtree_nodes = self._make_subtree(
                    left_partition)
            right_child, right_subtree_nodes = self._make_subtree(
                    right_partition)

            # Compute hashes of children.
            left_hash = None
            right_hash = None
            if left_child is not None:
                left_hash=self.object_store.hash_object(
                    left_child.serialize())
            if right_child is not None:
                right_hash=self.object_store.hash_object(
                    right_child.serialize())

            pivot_node = self.node_cls(
                    lookup_prefix=pivot_key,
                    left_hash=left_hash, right_hash=right_hash)

            return pivot_node, left_subtree_nodes + right_subtree_nodes

    def commit(self):
        """
        Commit items to the tree.

        :param items: An iterable of comparable and serializable items
        :type items: Byte string is best
        """
        items = sorted(self.items.items(), key=lambda t: t[0])
        head_node, subtree_nodes = self._make_subtree(items)
        for node in [head_node] + subtree_nodes:
            serialized_node = node.serialize()
            self.object_store.add(serialized_node)
        for serialized_obj in self.items.values():
            self.object_store.add(serialized_obj)
        head = self.object_store.hash_object(head_node.serialize())
