.. image:: https://raw.githubusercontent.com/spring-epfl/hippiepug/master/hippiepug.svg?sanitize=true
   :width: 100px
   :alt: Hippiepug

=========
hippiepug
=========

|pypi| |build_status| |test_cov| |docs_status|


Sublinear-lookup blockchains and efficient key-value Merkle trees.

Check out the `documentation <https://hippiepug.readthedocs.io/>`_.

.. |pypi| image:: https://img.shields.io/pypi/v/hippiepug.svg
   :target: https://pypi.org/project/hippiepug/
   :alt: PyPI version

.. |docs_status| image:: https://readthedocs.org/projects/hippiepug/badge/?version=latest
   :target: https://hippiepug.readthedocs.io/?badge=latest
   :alt: Documentation status

.. |build_status| image:: https://api.travis-ci.org/spring-epfl/hippiepug.svg?branch=master
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

You can install the library from PyPI:

.. code-block::  bash

   pip install hippiepug

To run the tests, you can do:

.. code-block::  bash

   python setup.py test

Acknowledgements
~~~~~~~~~~~~~~~~

* The library is a reimplementation of G. Danezis's `hippiehug`_ (hence the name).
* This work is funded by the `NEXTLEAP project`_ within the European Union’s Horizon 2020 Framework Programme for Research and Innovation (H2020-ICT-2015, ICT-10-2015) under grant agreement 688722.
* The hippie pug logo kindly donated by `M. Naiem`_.

.. _hippiehug:  https://github.com/gdanezis/rousseau-chain
.. _NEXTLEAP project:  https://nextleap.eu
.. _M. Naiem:  http://mariam.space
