"""
Building blocks.
"""
import attr

@attr.s
class ChainBlock(object):
    payload = attr.ib()
    index = attr.ib(default=0)
    fingers = attr.ib(default=attr.Factory(list))


@attr.s
class TreeNode(object):
    """Merkle tree intermediate node.

    :param pivot_key: Pivot key for the subtree
    :param left_hash: Hash of the left child
    :param right_hash: Hash of the right child
    """

    pivot_key = attr.ib()
    left_hash = attr.ib(default=None)
    right_hash = attr.ib(default=None)


@attr.s
class TreeLeaf(object):
    """Merkle tree leaf.

    :param lookup_key: Lookup key
    :param payload_hash: Hash of the payload
    """

    lookup_key = attr.ib(default=None)
    payload_hash = attr.ib(default=None)
