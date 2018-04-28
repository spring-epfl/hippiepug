"""
Tools for building and interpreting skipchains.
"""

from warnings import warn

from .struct import ChainBlock
from .pack import encode, decode


class Chain(object):
    """Skipchain (hash chain with skip-list pointers).

    To add a new block to a chain, use :py:class:`BlockBuilder`.

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
                block = self.chain[self.current_index]
                self.current_index -= 1
                return block
            else:
                raise StopIteration

        def next(self):
            return self.__next__()

    def __init__(self, object_store, head=None,
                 cache=None):
        """
        :param object_store: Object store
        :param head: The hash of the head block
        :param dict cache: Cache
        """
        self.object_store = object_store
        self.head = head
        self._cache = cache or {}

    @property
    def head_block(self):
        """The latest block in the chain."""
        return self._get_block_by_hash(self.head)

    def _get_block_by_hash(self, hash_value):
        """Unsafely retrieve block by its hash.

        .. warning::
            This function does not check if the retrieved block
            belongs to this chain.

        :raises: ``ValueError`` if retrieved object is not
                 a :py:class:`struct.ChainBlock`
        """
        if hash_value in self._cache:
            return self._cache[hash_value]

        serialized_block = self.object_store.get(hash_value)
        if serialized_block is not None:
            block = decode(serialized_block)
            if not isinstance(block, ChainBlock):
                raise ValueError('Object with this hash is not a chain block.')
            self._cache[hash_value] = block
            return block

    def get_block_by_index(self, index, return_proof=False):
        """Get block by index.

        Optionally returns inclusion proof, that is a list of intermediate
        blocks, sufficient to verify the inclusion of the retrieved block.

        :param int>=0 index: Block index
        :param bool return_proof: Whether to return inclusion proof
        :returns: Found block or None, or (block, proof) tuple if
                  return_proof is True.
        :raises: If the index is out of bounds,
                 raises ``IndexError``.
        """
        if self.head_block is None:
            if return_proof:
                return (None, [])
            return None
        if not (0 <= index <= self.head_block.index):
            raise IndexError(
                ("Block is beyond this chain head. Must be "
                 "0 <= {} <= {}.").format(index, self.head_block.index))

        proof = []
        hash_value = self.head
        current_block = self.head_block
        while True:
            if current_block is None:
                break

            try:
                proof.append(current_block)
                # When found:
                if index == current_block.index:
                    if return_proof:
                        return (current_block, proof)
                    return current_block
                # Otherwise, follow the fingers:
                _, hash_value = [(f, h) for (f, h) in current_block.fingers
                          if f >= index][0]
                current_block = self._get_block_by_hash(hash_value)

            # If something happened, likely a block was malformed.
            except Exception as e:
                warn('Exception occured while processing block %s: %s' % (
                    current_block, e))
                break

    def __getitem__(self, index):
        """Get block by index."""
        block = self.get_block_by_index(index, return_proof=False)
        if block is None:
            raise IndexError('Block not found.')
        return block

    def _append(self, block):
        """Append block to the chain."""
        serialized_block = encode(block)
        self.head = self.object_store.add(serialized_block)
        self._cache[self.head] = block

    def __iter__(self):
        return Chain.ChainIterator(self.head_block.index, self)

    def __repr__(self):
        return ('Chain('  # pragma: no cover
                'object_store={self.object_store}, '
                'head=\'{self.head}\')').format(
                    self=self)


class BlockBuilder(object):
    """Customizable builder of skipchain blocks.

    You can override the pre-commit hook (:py:func:`BlockBuilder.pre_commit`)
    to modify the payload before the block is committed to a chain. This
    is needed, say, if you want to sign the payload before commiting.

    :param chain: Chain to which the block should belong.

    Set the payload before committing:

    >>> from .store import Sha256DictStore
    >>> store = Sha256DictStore()
    >>> chain = Chain(store)
    >>> builder = BlockBuilder(chain)
    >>> builder.payload = b'Hello, world!'
    >>> block = builder.commit()
    >>> block == chain.head_block
    True
    """
    def __init__(self, chain):
        self._chain = chain
        self._block = self._make_next_block()

    @property
    def chain(self):
        """The associated chain."""
        return self._chain

    @property
    def payload(self):
        """Anticipated block payload."""
        return self._block.payload

    @payload.setter
    def payload(self, value):
        """Set the block payload.

        :param bytes value: Block payload
        """
        self._block.payload = value

    @property
    def index(self):
        """Anticipated index of the block being built."""
        return self._block.index

    @property
    def fingers(self):
        """Anticipated skip-list fingers (back-pointers to previous blocks)."""
        return self._block.fingers

    @staticmethod
    def skipchain_indices(index):
        """Finger indices for a given index.

        :param int>=0 index: Block index
        """
        return {index - 1 - ((index - 1) % (2**f)) for f in range(64)}

    def _make_next_block(self, payload=None):
        """Prepare an empty subsequent block.

        This method prefills the index and fingers. Payload is expected
        to be added before commiting to the chain.
        """

        new_block = ChainBlock(payload=payload)
        if self.chain.head is None:
            return new_block

        current_block = self.chain.head_block
        new_block.index = current_block.index + 1

        finger_indices = self.skipchain_indices(new_block.index)
        # NOTE: We want to use lists, and not tuples here, b/c
        #       msgpack transforms tuples into lists. So if these
        #       were tuples, comparison of fresh and deserialized
        #       blocks would be non-trivial.
        new_fingers = [[current_block.index, self.chain.head]]
        # TODO: Do we also need to generate new fingers here?
        for index, prev_hash in current_block.fingers:
            if index in finger_indices:
                new_fingers.append([index, prev_hash])

        new_block.fingers = new_fingers
        return new_block

    def commit(self):
        """Commit the block to the associated chain.

        :return: The block that was committed.
        """
        self.pre_commit()
        current_block = self._block
        self.chain._append(current_block)
        self._block = self._make_next_block()
        return current_block

    def pre_commit(self):
        """Pre-commit hook.

        This can be overriden. For example, you can add a signature
        that includes index and fingers into your payload before
        the block is committed.
        """
        pass

    def __repr__(self):
        return ('{self.__class__.__name__}('  # pragma: no cover
                'chain={self.chain}, '
                'payload=\'{self.payload}\')').format(
                    self=self)


def verify_chain_inclusion_proof(store, head, block, proof):
    """Verify inclusion proof for a block on a chain.

    :param store: Object store, may be empty
    :param head: Chain head
    :param block: Block
    :param proof: Inclusion proof
    :type proof: list of decoded blocks
    :returns: bool
    """
    for other_block in proof:
        store.add(encode(other_block))
    verifier_chain = Chain(store, head=head)
    retrieved_block = verifier_chain.get_block_by_index(block.index)
    return retrieved_block == block

