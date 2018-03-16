import abc

from . import utils


class BaseStore(object):
    """Abstract base class for a content-addresable store."""

    __metadata__ = abc.ABCMeta

    @abc.abstractmethod
    def __contains__(self, obj_hash):
        """Check whether the store contains an object with a give hash.

        @param obj_hash: ASCII hash
        """
        pass

    @abc.abstractmethod
    def get(self, obj_hash, check_integrity=True):
        """Return the object by its ASCII hash value.

        @param obj_hash: ASCII hash
        @param check_integrity: Whether to check the hash upon retrieval
        """
        pass

    @abc.abstractmethod
    def add(self, serialized_obj):
        """
        Put the object in the store.

        @param serialized_obj: Byte string object
        """
        pass


class MemoryStore(BaseStore):
    """
    In-memory object store.

    >>> store = MemoryStore()
    >>> obj = b'A'
    >>> obj_hash = utils.ascii_hash(obj)
    >>> store.add(obj)
    >>> obj_hash in store
    True
    >>> b'nonexistent' in store
    False
    >>> store.get(obj_hash) == obj
    True
    """

    def __init__(self, backend=None):
        """
        Build a store using a dict-like backend.

        @param backend: dict-like object
        """
        if backend is None:
            backend = {}
        self._backend = backend

    def __contains__(self, obj_hash):
        return self.get(obj_hash, check_integrity=False) is not None

    def get(self, obj_hash, check_integrity=True):
        """Get an object with a given hash from the store.

        If the object does not exist, returns None.

        :param obj_hash: ASCII hash of the object
        :param check_integrity: Whether to check the hash of the retrieved
                                object with the given hash.
        """
        serialized_obj = self._backend.get(obj_hash)
        if serialized_obj is not None and check_integrity:
            utils.check_hash(obj_hash, serialized_obj)
        return serialized_obj

    def add(self, serialized_obj):
        """Add an object to the store.

        If an object with this hash already exists, silently does nothing.
        """
        obj_hash = utils.ascii_hash(serialized_obj)
        if not obj_hash in self:
            self._backend[obj_hash] = serialized_obj

    def __repr__(self):
        return '{self.__class__.__name__}(backend={self._backend})'.format(
            self=self)
