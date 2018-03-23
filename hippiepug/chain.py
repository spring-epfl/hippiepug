import abc
import collections

import msgpack

from .block import Block
from .store import Sha256DictStore
from .pack import encode, decode


class Chain(object):
    """Verifiable deterministic skip-chain.

    This class handles all interactions with the backend. It also supports
    customizable blocks to which you can add some complex behaviour.

    Skip-chain is considered mutable, that is you should always be able to
    append a new block to a given chain. The interface is thus different from
    Trees, that are constructed once, and then are immutable.

    .. warning::
       All read accesses are cached. The cache is assumed to be trusted,
       so blocks retrieved from cache are not checked for integrity, unlike
       when they are retrieved from the object store.

    .. seealso::
       * :py:class:`hippiepug.tree.Tree`
    """

    class ChainIterator(object):
        """
        Chain iterator.

        .. note::
           Iterates in the reverse order: latest block first.
        """
        def __init__(self, current_index, chain):
            self.current_index = current_index
            self.chain = chain

        def __next__(self):
            if self.current_index >= 0:
                block = self.chain.get_block_by_index(self.current_index)
                self.current_index -= 1
                return block
            else:
                raise StopIteration

        def next(self):
            return self.__next__()

    def __init__(self, block_cls=None, object_store=None, head=None,
                 cache=None):
        """
        :param block_cls: Block class
        :param object_store: Object store
        :param head: The hash of the head block
        :param cache: Cache
        :type cache: ``dict``
        """
        self._block_cls = block_cls
        if object_store is None:
            object_store = Sha256DictStore()
        self.object_store = object_store
        self.head = head
        self._cache = cache or {}

    @property
    def head_block(self):
        """The latest block in the chain."""
        return self.get_block_by_hash(self.head)

    def get_block_cls(self):
        """Return the block class."""

        if self._block_cls is not None:
            return self._block_cls
        elif hasattr(self, 'block_cls') and self.block_cls is not None:
            return self.block_cls
        else:
            raise TypeError('Block class not defined.')

    def make_next_block(self, *args, **kwargs):
        """Prepare the next block in the chain."""
        return self.get_block_cls()._make_next_block(
            current_block=self.head_block, chain=self, is_read_only=False,
            *args, **kwargs)

    def get_block_by_hash(self, hash_value):
        """Retrieve block by its hash.

        :param hash_value: ASCII hash of the block
        """
        if hash_value in self._cache:
            return self._cache[hash_value]

        serialized_block = self.object_store.get(hash_value)
        if serialized_block is not None:
            block = decode(serialized_block)
            self._cache[hash_value] = block
            return block

    def get_block_by_index(self, index, return_evidence=False):
        """Retrieve a block by its index.

        Optionally returns inclusion evidence, that is a list of intermediate
        blocks, sufficient to verify the includion of the retrieved block.

        If the block is not found, returns None. If the index is out of bounds,
        raises IndexError.

        :param index: Block index
        :param return_evidence: Whether to return evidence
        :return: Found block or None, or (block, evidence) tuple if
                 return_evidence is True.
        """
        if self.head is None:
            return None
        if return_evidence:
            evidence = []
        if not (0 <= index <= self.head_block.index):
            raise IndexError(
                ("Block is beyond this chain head. Must be "
                 "0 <= {} <= {}.").format(index, self.head_block.index))

        hash_value = self.head
        current_block = self.head_block
        while current_block is not None:
            if return_evidence:
                evidence.append(current_block)
            # When found:
            if index == current_block.index:
                if return_evidence:
                    return (current_block, evidence)
                return current_block
            # Otherwise, follow the fingers:
            _, hash_value = [(f, h) for (f, h) in current_block.fingers
                      if f >= index][0]
            current_block = self.get_block_by_hash(hash_value)

    def _commit_block(self, block):
        """Commit new block to the object store."""
        serialized_block = encode(block)
        self.head = self.object_store.hash_object(serialized_block)
        self._cache[self.head] = block
        self.object_store.add(serialized_block)
        return self.head

    def __iter__(self):
        return Chain.ChainIterator(self.head_block.index, self)

    def __repr__(self):
        return ('{self.__class__.__name__}('
                'block_cls={block_cls}, '
                'object_store={self.object_store}, '
                'head=\'{self.head}\')').format(
            self=self, block_cls=self.get_block_cls())
