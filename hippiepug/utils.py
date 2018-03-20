# -*- coding: utf-8 -*-

import abc
import six
import threading
import contextlib

from hashlib import sha256
from binascii import hexlify


def sha256_ascii_hash(item):
    """
    >>> sha256_ascii_hash(b'value')[:4] == 'cd42'
    True
    """
    return sha256(item).hexdigest()


class Serializable(object):
    """Serializable object interface."""
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self):
        """Serialize obj, in particular for hashing or storing."""
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, serialized_obj):
        """Deserialize obj."""
        pass


class DummySerializableObject(Serializable):
    def __init__(self, obj):
        self.obj = obj

    def serialize(self):
        return self.obj

    def deserialize(cls, serialized_obj):
        return cls(serialized_obj)
