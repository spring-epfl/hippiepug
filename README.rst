.. image:: https://raw.githubusercontent.com/spring-epfl/hippiepug/master/hippiepug.svg?sanitize=true
   :width: 100px
   :alt: Hippiepug

=========
hippiepug
=========

|pypi| |dev_status| |build_status| |test_cov| |docs_status| 

|

Sublinear-lookup blockchains and efficient key-value Merkle trees. Check out the `documentation <https://hippiepug.readthedocs.io/>`_.

.. |pypi| image:: https://img.shields.io/pypi/v/hippiepug.svg
   :target: https://pypi.org/project/hippiepug/
   :alt: PyPI version

.. |dev_status| image:: https://img.shields.io/pypi/status/hippiepug.svg
   :target: https://pypi.org/project/hippiepug/
   :alt: Development status

.. |docs_status| image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
   :target: https://hippiepug.readthedocs.io/?badge=latest
   :alt: Documentation status

.. |build_status| image:: https://travis-ci.org/bogdan-kulynych/hippiepug.svg?branch=master
   :target: https://travis-ci.org/bogdan-kulynych/hippiepug
   :alt: Build status

.. |test_cov| image:: https://coveralls.io/repos/github/bogdan-kulynych/hippiepug/badge.svg
   :target: https://coveralls.io/github/bogdan-kulynych/hippiepug
   :alt: Test coverage

--------------

.. inclusion-marker-do-not-remove

This library provides implementations of two cryptographic data structures:

- Blockchains with log(n) lookups, implemented as deterministic hash skipchains. In this kind of blockchain verifying that block *b* extends block *a* does not require to download and process all blocks between *a* and *b*, but only a logarithmic amount of blocks.
- Verifiable unique-resolution dictionary, implemented as a key-value Merkle tree.

Both are meant to be used with a content-addressable storage. Each data structure supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+
|                       | Retrievals per lookup    | Inclusion proof size | Append         |
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
