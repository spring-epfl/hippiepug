import collections

from attr import attrs, attrib
from .utils import HashableMixin


@attrs
class Node(HashableMixin):
    """Merkle tree node."""
    prefix = attrib(default=None)
    payload = attrib(default=None)
    left_hid = attrib(default=None)
    right_hid = attrib(default=None)

    @property
    def is_leaf(self):
        return self.left_hid is None and self.right_hid is None

    def serialize(self):
        """Serialize node, in particular for hashing."""
        return msgpack.packb(
                (self.prefix, self.payload, self.left_hid, self.right_hid),
                use_bin_type=True)

    @classmethod
    def deserialize(cls, serialized_node):
        """Deserialize node."""
        prefix, payload, left_hid, right_hid = msgpack.unpackb(
                serialized_node, raw=False)
        return cls(prefix, payload, left_hid, right_hid)


class Tree(object):
    def __init__(self, object_store, head,
                 _cache=None):
        """
        :param object_store: Object store
        :param head: The hash of the head block
        :param _cache: Cache
        :type _cache: dict
        """
        self.object_store = object_store
        self.head = head
        self._cache = _cache or {}

    def get_node_by_hid(self, hid):
        if hid in self._cache:
            return self._cache[hid]

        raw_node = self.object_store.get(hid, check_integrity=True)
        if raw_node is not None:
            node = Node.deserialize(raw_node)
            self._cache[hid] = block

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
        return self._backend.get(self.head)


class TreeBuilder(object):
    """Verifiable Merkle tree, backed by an object store.

    This class handles all interactions with the backend.

    .. warning::
       All read accesses are cached. The cache is assumed to be trusted,
       so blocks retrieved from cache are not checked for integrity, unlike
       when they are retrieved from the object store.

       :param object_store: Object store

    .. seealso::
       * :py:class:`hippiepug.chain.Chain`
    """

    def __init__(self, object_store=None):
        self.object_store = object_store

    def _make_subtree(self, items):
        """Build a tree from sorted items."""
        if len(items) == 0:
            return None, []
        if len(items) == 1:
            item = next(items)
            return Node(item), []
        else:
            middle = len(items) // 2
            pivot = items[middle]
            left_partition = items[:middle]
            right_partition = items[middle+1:]
            left_child, left_subtree_nodes = self._make_subtree(
                    left_partition)
            right_child, right_subtree_nodes = self._make_subtree(
                    right_partition)
            pivot_node = IntermediateNode(left_child.hid, right_child.hid)
            return pivot_node, left_subtree_nodes + right_subtree_nodes

    def commit(self):
        """
        Commit items to the tree.

        :param items: An iterable of comparable and serializable items
        :type items: Byte string is best
        """
        items = sorted(items)
        head_node, subtree_nodes = self._make_subtree(items)
        self.head = head_node.hid
        for node in [head_node] + subtree_nodes:
            serialized_node = node.serialize()
            self._backend.add(serialized_node)
            assert self._backend.get(node.hid) == serialized_node
