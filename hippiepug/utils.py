# -*- coding: utf-8 -*-

import abc
import six
import threading
import contextlib

from hashlib import sha256
from binascii import hexlify


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
