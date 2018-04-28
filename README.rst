.. image:: https://raw.githubusercontent.com/spring-epfl/hippiepug/master/hippiepug.svg?sanitize=true
   :width: 100px
   :alt: Hippiepug

#########
hippiepug
#########

|pypi| |build_status| |test_cov| |docs_status| |license|


Sublinear-lookup blockchains and efficient key-value Merkle trees.

Check out the `documentation <https://hippiepug.readthedocs.io/>`_.

.. |pypi| image:: https://img.shields.io/pypi/v/hippiepug.svg
   :target: https://pypi.org/project/hippiepug/
   :alt: PyPI version

.. |license| image:: https://img.shields.io/pypi/l/hippiepug.svg
   :target: https://pypi.org/project/hippiepug/
   :alt: License

.. |docs_status| image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
   :target: https://hippiepug.readthedocs.io/?badge=latest
   :alt: Documentation status

.. |build_status| image:: https://api.travis-ci.org/spring-epfl/hippiepug.svg?branch=master
   :target: https://travis-ci.org/spring-epfl/hippiepug
   :alt: Build status

.. |test_cov| image:: https://coveralls.io/repos/github/spring-epfl/hippiepug/badge.svg
   :target: https://coveralls.io/github/spring-epfl/hippiepug
   :alt: Test coverage

--------------

.. description-marker-do-not-remove

This library provides implementations of two cryptographic data structures:

- Blockchains with log(n) sublinear traversal, implemented as high-integrity
  deterministic skip-lists (skipchains). In this kind of blockchain verifying
  that block *b* extends block *a* does not require to download and process
  all blocks between *a* and *b*, but only a logarithmic amount of them.
- Verifiable dictionary, implemented as a key-value Merkle tree that
  guarantees unique resolution. A proof of inclusion of a key-value pair in
  such a tree also proves that there does not exist another value for a given
  key somewhere else in the tree.

Both are meant to be used with a content-addressable storage. Each data
structure supports logarithmic queries, and logarithmic proofs of inclusion:

+-----------------------+--------------------------+----------------------+----------------+
|                       | Retrievals per lookup    | Inclusion proof size | Append         |
+=======================+==========================+======================+================+
| Hash skipchain        | O(log(n))                | O(log(n))            | O(1)           |
+-----------------------+--------------------------+----------------------+----------------+
| Merkle key-value tree | O(log(n))                | O(log(n))            | Immutable      |
+-----------------------+--------------------------+----------------------+----------------+

with *n* being the size of the dictionary, or the number of blocks in the
case of a chain.

.. getting-started-marker-do-not-remove

===============
Getting started
===============

You can install the library from PyPI:

.. code-block::  bash

   pip install hippiepug

Then, the easiest way to run the tests is:

.. code-block::  bash

   python setup.py test

Be sure to check out the `usage guide <https://hippiepug.readthedocs.org/usage.html>`_.

.. acks-marker-do-not-remove

================
Acknowledgements
================

* The library is a reimplementation of G. Danezis's `hippiehug`_ (hence
  the name).
* This work is funded by the `NEXTLEAP project`_ within the European Union’s
  Horizon 2020 Framework Programme for Research and Innovation (H2020-ICT-2015,
  ICT-10-2015) under grant agreement 688722.
* The hippie pug logo kindly donated by `M. Naiem`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain
.. _NEXTLEAP project:  https://nextleap.eu
.. _M. Naiem:  http://mariam.space
