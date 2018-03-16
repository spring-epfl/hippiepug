# -*- coding: utf-8 -*-

import doctest
import six
import threading
import contextlib

from hashlib import sha256 as hash_fn
from binascii import hexlify


doctest.IGNORE_EXCEPTION_DETAIL = True


class IntegrityValidationError(Exception):
    pass


def binary_hash(item):
    """
    >>> binary_hash(b'value')[:4] == six.b('\xcdB@M')
    True
    """
    return hash_fn(item).digest()


def ascii_hash(item):
    """
    >>> ascii_hash(b'value')[:4] == six.u('cd42')
    True
    """
    return hexlify(binary_hash(item)).decode('utf-8')


class HashableMixin(object):
    @property
    def hid(self):
        """Return the hash of a serializable object."""
        serialized = self.serialize()
        return ascii_hash(serialized)

    def __eq__(self, other):
        return self.hid == other.hid


def check_hash(hash_value, item):
    """
    >>> a = b'Correct.'
    >>> b = b'Incorrect'
    >>> h = ascii_hash(a)
    >>> check_hash(h, a)
    >>> check_hash(h, b)
    Traceback (most recent call last):
        ...
    IntegrityValidationError: Object hash mismatch.
    """
    if hash_value != ascii_hash(item):
        raise IntegrityValidationError('Object hash mismatch.')
