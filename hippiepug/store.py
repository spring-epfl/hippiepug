import abc
from binascii import hexlify

from hashlib import sha256


class BaseStore(object):
    """Abstract base class for a content-addresable store."""
    __metaclass__ = abc.ABCMeta

    @classmethod
    @abc.abstractmethod
    def hash_object(cls, serialized_obj):
        """Return the ASCII hash of the object.

        :param obj: Object, serialized to bytes
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def __contains__(self, obj_hash):
        """Check whether the store contains an object with a give hash.

        :param obj_hash: ASCII hash
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get(self, obj_hash, check_integrity=True):
        """Return the object by its ASCII hash value.

        :param obj_hash: ASCII hash
        :param check_integrity: Whether to check the hash upon retrieval
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def add(self, serialized_obj):
        """
        Put the object in the store.

        :param serialized_obj: Object, serialized to bytes
        :return: Hash of the object.
        """
        pass  # pragma: no cover


class IntegrityValidationError(Exception):
    pass


class BaseDictStore(BaseStore):
    """
    Store with dict-like backend.

    :param backend: Backend
    :type backend: dict-like
    """

    def __init__(self, backend=None):
        if backend is None:
            backend = {}
        self._backend = backend

    def __contains__(self, obj_hash):
        """Check if obj with a given hash is in the store."""
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
        return obj_hash

    def __repr__(self):
        return ('{self.__class__.__name__}('
                '{self._backend})').format(self=self)  # pragma: no cover


class Sha256DictStore(BaseDictStore):
    """
    Dict-based store using truncated SHA256 hex-encoded hashes.

    >>> store = Sha256DictStore()
    >>> obj = b'dummy'
    >>> obj_hash = store.hash_object(obj)
    >>> store.add(obj) == obj_hash
    True
    >>> obj_hash in store
    True
    >>> b'nonexistent' not in store
    True
    >>> store.get(obj_hash) == obj
    True
    """

    HASH_SIZE_BYTES = 8

    def hash_object(cls, serialized_obj):
        """Return a SHA256 hex-encoded hash of a serialized object."""
        hash_bytes = sha256(serialized_obj).digest()
        hexdigest = hexlify(hash_bytes[:Sha256DictStore.HASH_SIZE_BYTES])
        return hexdigest.decode('utf-8')
