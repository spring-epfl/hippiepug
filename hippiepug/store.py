import abc

from . import utils


class BaseStore(object):
    """Abstract base class for a content-addresable store."""
    __metaclass__ = abc.ABCMeta

    @classmethod
    @abc.abstractmethod
    def hash_object(cls, serialized_obj):
        """Return the ASCII hash of the object.

        :param obj: Object, serialized to bytes
        """
        pass

    @abc.abstractmethod
    def __contains__(self, obj_hash):
        """Check whether the store contains an object with a give hash.

        :param obj_hash: ASCII hash
        """
        pass

    @abc.abstractmethod
    def get(self, obj_hash, check_integrity=True):
        """Return the object by its ASCII hash value.

        :param obj_hash: ASCII hash
        :param check_integrity: Whether to check the hash upon retrieval
        """
        pass

    @abc.abstractmethod
    def add(self, serialized_obj):
        """
        Put the object in the store.

        :param serialized_obj: Object, serialized to bytes
        """
        pass


class Sha256HashMixin(object):
    def hash_object(cls, serialized_obj):
        """SHA256 hex hash of a serialized object."""
        return utils.sha256_ascii_hash(serialized_obj)


class IntegrityValidationError(Exception):
    pass


class DictStore(Sha256HashMixin, BaseStore):
    """
    Store using SHA256 hash function and dict-like backend.

    :param backend: dict-like object

    >>> store = DictStore()
    >>> obj = b'dummy'
    >>> obj_hash = utils.sha256_ascii_hash(obj)
    >>> store.add(obj)
    >>> obj_hash in store
    True
    >>> b'nonexistent' in store
    False
    >>> store.get(obj_hash) == obj
    True
    """

    def __init__(self, backend=None):
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
                                object against the given hash.
        """
        serialized_obj = self._backend.get(obj_hash)
        if serialized_obj is not None and check_integrity:
            if obj_hash != self.hash_object(serialized_obj):
                raise IntegrityValidationError()
        return serialized_obj

    def add(self, serialized_obj):
        """Add an object to the store.

        If an object with this hash already exists, silently does nothing.
        """
        obj_hash = self.hash_object(serialized_obj)
        if not obj_hash in self:
            self._backend[obj_hash] = serialized_obj

    def __repr__(self):
        return '{self.__class__.__name__}({self._backend})'.format(
            self=self)
