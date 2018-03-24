hippiepug
=========

Sublinear-traversal blockchains and efficient key-value Merkle trees 

:Documentation:
    .. image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
       :target: https://hippiepug.readthedocs.io/?badge=latest
       :alt: Documentation Status

:Build status:
    .. image:: https://travis-ci.org/bogdan-kulynych/hippiepug.svg?branch=master
       :target: https://travis-ci.org/bogdan-kulynych/hippiepug
       :alt: Build status

:Test coverage:
    .. image:: https://coveralls.io/repos/github/bogdan-kulynych/hippiepug/badge.svg
       :target: https://coveralls.io/github/bogdan-kulynych/hippiepug
       :alt: Test coverage

--------------

.. inclusion-marker-do-not-remove

This library provides implementations of two cryptographic data structures:

- Blockchains with log(n) sublinear traversal, implemented as deterministic hash skipchains
- Verifiable unique-resolution dictionary, implemented as a key-value Merkle tree
    
Both are meant to be used with a content-addressable storage. Each data structures supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+
|                       | Retrievals per query     | Inclusion proof size | Append         |
+=======================+==========================+======================+================+
| Hash skipchain        | ~log(n)                  | O(log(n))            | O(1)           |
+-----------------------+--------------------------+----------------------+----------------+
| Merkle key-value tree | ~log(n)                  | O(log(n))            | Immutable      |
+-----------------------+--------------------------+----------------------+----------------+

with *n* being the size of the dictionary, or the number of blocks in the case of a chain.

Acknowledgements
~~~~~~~~~~~~~~~~

The library is a reimplementation of G. Danezis's `hippiehug`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain

