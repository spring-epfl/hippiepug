hippiepug
=========

Sublinear-traversal blockchains and efficient key-value Merkle trees 

.. image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
   :target: http://hippiepug.readthedocs.io/?badge=latest
   :alt: Documentation Status
.. image:: https://travis-ci.org/bogdan-kulynych/hippiepug.svg?branch=master
   :target: https://travis-ci.org/bogdan-kulynych/hippiepug
   :alt: Build status
.. image:: https://coveralls.io/repos/github/bogdan-kulynych/hippiepug/badge.svg
   :target: https://coveralls.io/github/bogdan-kulynych/hippiepug
   :alt: Test coverage

--------------

.. inclusion-marker-do-not-remove

This library provides implementations of two cryptographic data structures:

  * Blockchains with log(n) sublinear traversal, implemented as deterministic hash skipchains
  * Verifiable unique-resolution dictionary, implemented as a Merkle prefix tree
    
Both are meant to be used with a content-addressable storage. Each data structures supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+---------------------+
|                       | Retrievals per query     | Inclusion proof size | Append         | Data structure size |
+=======================+==========================+======================+================+=====================+
| Hash skipchain        | ~log(n)                  | O(log(n))            | O(1)           | O(n)                |
+-----------------------+--------------------------+----------------------+----------------+---------------------+
| Merkle prefix tree    | ~log(n)                  | O(log(n))            | Immutable      | O(n)                |
+-----------------------+--------------------------+----------------------+----------------+---------------------+


with *n* being the size of the dictionary, or the number of blocks in the case of a chain.

Acks
----

The library is a reimplementation of G. Danezis's `hippiehug`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain

