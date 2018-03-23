hippiepug
=========

Efficient Merkle trees and log(n) hash chains.

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

This library provides implementations of three cryptographiic data structures: hash skipchain, verifiable unique-resolution dictionary, and verifiable set, that are meant to be used on top of a content-addressable storage.
Each of the data structures supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+---------------------+
|                       | Retrievals per query     | Inclusion proof size | Append         | Data structure size |
+=======================+==========================+======================+================+=====================+
| Hash skipchain        | log(n)                   | O(log(n))            | O(1)           | O(n)                |
+-----------------------+--------------------------+----------------------+----------------+---------------------+
| Verifiable dictionary | log(n)                   | O(log(n))            | Immutable      | O(n)                |
+-----------------------+--------------------------+----------------------+----------------+---------------------+
| Verifiable set        | log(n)                   | O(log(n))            | Immutable      | O(n)                |
+-----------------------+--------------------------+----------------------+----------------+---------------------+


with *n* being the size for the map and the set, or the number of blocks in the case of a chain.

---------------

Acknowledgement
===============

The library is a reimplementation of G. Danezis's `hippiehug`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain

