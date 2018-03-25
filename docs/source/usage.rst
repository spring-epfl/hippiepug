===========
Usage guide
===========

Storage
-------

We call *content-addressable storage* a key-value store in which keys are cryptographic hashes of blocks or nodes, and values are the blocks or the nodes. When components of hash chains and Merkle trees are stored in such store, queriers only need to verify integrity of values retrieved from the stores, and do not need to verify paths.

``hippiepug`` includes an in-memory instantation of a content-addressable storage that uses SHA256 for hashes, by default truncating them to 8 bytes: :py:class:`hippiepug.store.Sha256DictStore`.

.. code-block::  python

    from hippiepug.store import Sha256DictStore

    store = Sha256DictStore()
    obj = b'dummy'
    obj_hash = store.hash_object(obj)  # 'b5a2c96250612366'

    store.add(obj) == obj_hash  # True

The store verifies hashes internally on each lookup.

.. code-block::  python

    obj_hash in store  # True
    store.get(obj_hash) == obj   # True

You can define a completely store by overriding abstract base :py:class:`hippiepug.store.BaseStore`. You can also implement ``hash_object`` method in :py:class:`hippiepug.store.BaseDictStore` to return other hash function values, to have an in-memory store like the default one.


Building chains
---------------

To build a chain, first obtain a chain from somewhere, or initialize a new empty :py:class:`hippiepug.chain.Chain` object.

.. code-block::  python

    from hippiepug.chain import Chain

    chain = Chain(store)
    chain.head  # None


Then, add chain blocks ony by one.

.. code-block::  python

    from hippiepug.chain import BlockBuilder

    block_builder = BlockBuilder(chain)
    block_builder.payload = b'This is the first block!'
    block_builder.commit()

    chain.head  # '154bdee593d8c9b2'

You can then continue adding blocks using the same builder instance.

.. code-block::  python

    block_builder.payload  # None
    block_builder.payload = b'This is the second block!'
    block_builder.commit()

    chain.head  # '48e399de59796ab1'

The builder automatically adds all the skipchain special fields, like hashes of previous blocks.


Building trees
--------------

Unlike chains, ``hippepug`` trees can not be extended. To build a new tree, initialize the tree builder on a store, and set the key-value pairs to be committed.

.. code-block::  python
    from hippiepug.tree import TreeBuilder

    tree_builder = TreeBuilder(store)
    tree_builder['foo'] = b'bar'
    tree_builder['baz'] = b'wow'

Once all key-value pairs, commit them to store and obtain a view of the committed tree:

.. code-block::  python

    tree = tree_builder.commit()
    tree.root  # '150cc8da6d6cfa17'
    'foo' in tree  # True
    'baz' in tree  # True


Querying and verifying
----------------------

TODO
