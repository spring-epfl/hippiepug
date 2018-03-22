import abc
import collections

import msgpack

from .utils import Serializable
from .store import Sha256DictStore


class BaseBlock(Serializable):
    """
    Customizable base skip-list block.

    You can override the pre-commit hook (:py:func:`BaseBlock.pre_commit``)
    to modify the payload before the block is committed to a chain. This
    is needed, say, if you want to sign the payload before commiting.

    :param payload: Block payload
    :type payload: Byte array

    :param index: Sequence index
    :param fingers: Skip-list fingers (list of back-pointers to
                     previous blocks)
    :param hash_value: Block hash, if the block has been committed.
    :param is_read_only: Whether block can be committed.
    :param chain: Chain to which the block should belong.

    .. warning::
        You need to take extra care when defining custom serializations. Be
        sure that your serialization includes:

        - ``self.index``
        - ``self.fingers``
        - Your payload

        Unless this is done, the security of the hash chain is screwed.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, payload=None, index=0, fingers=None, chain=None,
                 hash_value=None, is_read_only=True):
        self.payload = payload
        self._index = index
        if fingers is None:
            fingers = []
        self._fingers = fingers
        self._chain = chain
        self._hash_value = hash_value
        self._is_read_only = is_read_only

    @property
    def index(self):
        return self._index

    @property
    def fingers(self):
       return self._fingers

    @property
    def is_read_only(self):
        return self._is_read_only

    def __repr__(self):
        return ('{self.__class__.__name__}(_index={self.index}, '
                '_fingers={self.fingers}, _chain={self._chain}, '
                '_is_read_only={self.is_read_only}, '
                'payload="{self.payload}")').format(self=self)

    @classmethod
    def _make_next_block(cls, current_block, *args, **kwargs):
        """Build an empty subsequent block.

        .. warning::
            Use :py:func:`Chain.make_next_block`
            unless you know what you are doing.

        This method prefills the index and fingers. Payload is expected
        to be added before commiting to the chain.
        """

        if current_block is None:
            return cls(index=0, fingers=None, *args, **kwargs)

        new_index = current_block.index + 1
        new_fingers = [(current_block.index, current_block.hash_value)]

        finger_indices = BaseBlock.skipchain_indices(new_index)
        new_fingers += [f for f in current_block.fingers if f[0]
                        in finger_indices]

        new_block = cls(index=new_index, fingers=new_fingers,
                        *args, **kwargs)
        return new_block

    @staticmethod
    def skipchain_indices(index):
        """Finger indices for the current index."""
        return set(index - 1 - ((index - 1) % (2**f)) for f in range(64))

    @property
    def hash_value(self):
        return self._hash_value

    def commit(self):
        """Commit the block to the associated chain."""
        if self._is_read_only:
            raise TypeError('Block is read-only.')
        if self._chain is None:
            raise ValueError('Chain undefined.')

        self.pre_commit()
        self._hash_value = self._chain._commit_block(self)
        self._is_read_only = True

    def pre_commit(self):
        """Pre-commit hook.

        This can be overriden. For example, you can add a signature
        that includes index and fingers into your payload before
        the block is committed.
        """
        pass


class MsgpackBlock(BaseBlock):
    """Block that is msgpack-serializable."""

    def serialize(self):
        """Serialize."""
        return msgpack.packb((self.index, self.fingers, self.payload),
                             use_bin_type=True)

    @classmethod
    def deserialize(cls, serialized_block):
        """Deserialize."""
        index, fingers, payload = msgpack.unpackb(serialized_block, raw=False)
        return cls(payload, index=index, fingers=fingers)


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

        raw_block = self.object_store.get(hash_value)
        if raw_block is not None:
            block = self.get_block_cls().deserialize(raw_block)
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
        self.head = self.object_store.hash_object(block.serialize())
        self._cache[self.head] = block
        self.object_store.add(block.serialize())
        return self.head

    def __iter__(self):
        return Chain.ChainIterator(self.head_block.index, self)

    def __repr__(self):
        return ('{self.__class__.__name__}('
                'block_cls={block_cls}, '
                'object_store={self.object_store}, '
                'head=\'{self.head}\')').format(
            self=self, block_cls=self.get_block_cls())
