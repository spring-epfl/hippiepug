"""
Hashchain blocks.

The interface of a chain block is very different from tree nodes. Whereas tree
nodes are containers, and the :py:class:`tree.TreeMapBuilder` handles committing
the nodes into the store, ... TODO: finish.
"""

class Block(object):
    """
    Customizable base skipchain block.

    You can override the pre-commit hook (:py:func:`Block.pre_commit``)
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

        finger_indices = Block.skipchain_indices(new_index)
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
