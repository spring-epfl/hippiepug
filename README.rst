.. image:: hippiepug.svg
   :width: 100px
   :alt: Hippiepug

=========
hippiepug
=========

*Sublinear-traversal blockchains and efficient key-value Merkle trees*

+------------------------------------------------------+----------------+---------------+
| `Documentation <https://hippiepug.readthedocs.io/>`_ | Build status   | Test coverage |
+======================================================+================+===============+
| |docs_status|                                        | |build_status| | |test_cov|    |
+------------------------------------------------------+----------------+---------------+

.. |docs_status| image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
   :target: https://hippiepug.readthedocs.io/?badge=latest
   :alt: Documentation Status

.. |build_status| image:: https://travis-ci.org/bogdan-kulynych/hippiepug.svg?branch=master
   :target: https://travis-ci.org/bogdan-kulynych/hippiepug
   :alt: Build status

.. |test_cov| image:: https://coveralls.io/repos/github/bogdan-kulynych/hippiepug/badge.svg
   :target: https://coveralls.io/github/bogdan-kulynych/hippiepug
   :alt: Test coverage

--------------

.. inclusion-marker-do-not-remove

This library provides implementations of two cryptographic data structures:

- Blockchains with log(n) sublinear traversal, implemented as deterministic hash skipchains. In this kind of blockchain verifying that block *b* extends block *a* does not require to download and process all blocks between *a* and *b*, but only a logarithmic amount of blocks.
- Verifiable unique-resolution dictionary, implemented as a key-value Merkle tree.

Both are meant to be used with a content-addressable storage. Each data structure supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+
|                       | Retrievals per query     | Inclusion proof size | Append         |
+=======================+==========================+======================+================+
| Hash skipchain        | ~ log(n)                 | ~ log(n)             | O(1)           |
+-----------------------+--------------------------+----------------------+----------------+
| Merkle key-value tree | ~ log(n)                 | ~ 2log(n)            | Immutable      |
+-----------------------+--------------------------+----------------------+----------------+

with *n* being the size of the dictionary, or the number of blocks in the case of a chain.

Getting started
~~~~~~~~~~~~~~~

You can install the library directly from Github by running the following command:

.. code-block::  bash

   pip install -e git+git@github.com:bogdan-kulynych/hippiepug.git#egg=hippiepug

To run the tests, you can do:

.. code-block::  bash

   python setup.py test

Acknowledgements
~~~~~~~~~~~~~~~~

The library is a reimplementation of G. Danezis's `hippiehug`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain

