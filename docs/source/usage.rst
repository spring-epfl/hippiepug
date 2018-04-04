===========
Usage guide
===========

Storage
-------

We call *content-addressable storage* a key-value store in which keys are
cryptographic hashes of blocks or nodes, and values are the blocks or
the nodes. Using such storage with ``hippiepug`` is convenient, because a
creator of a data structure only needs to provide a querier a hash of
a chain head or tree root. That is, there is no need explicitly to produce
an inclusion proof. Queriers will be able to verify inclusion on the fly,
provided the storage is available. See section :ref:`proofs` for details.

``hippiepug`` includes an instantation of an in-memory content-addressable
storage that uses SHA256 for hashes, by default truncating them to
8 bytes: :py:class:`hippiepug.store.Sha256DictStore`.

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

If you want to use external storage, provide a dict-like facade to it
and pass as ``backend``:

.. code-block::  python

    class CustomBackend(object):

        def get(self, k):
            return 'stub'

        def __setitem__(self, k, v):
            pass

    store = Sha256DictStore(backend=CustomBackend())

To change the hash function, subclass :py:class:`hippiepug.store.BaseDictStore`,
and implement the ``hash_object`` function. You can
also define a completely different store by implementing abstract base
:py:class:`hippiepug.store.BaseStore`.

Building the data structures
----------------------------

Chain
~~~~~

To append a block to a chain, first obtain an existing chain from somewhere,
or initialize a new empty :py:class:`hippiepug.chain.Chain` object:

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

The builder automatically adds all the skipchain special fields, like
hashes of previous blocks.


Tree
~~~~

Unlike chains, ``hippepug`` trees can not be extended. To build a new tree,
initialize the tree builder on a store, and set the key-value pairs to be
committed.

.. code-block::  python

    from hippiepug.tree import TreeBuilder

    tree_builder = TreeBuilder(store)
    tree_builder['foo'] = b'bar'
    tree_builder['baz'] = b'wow'

Once all key-value pairs, commit them to store and obtain a view of the
committed tree:

.. code-block::  python

    tree = tree_builder.commit()
    tree.root  # '150cc8da6d6cfa17'


Querying the data structures
----------------------------

Chain
~~~~~

To get a queryable view of a chain, you need to specify the storage where the
blocks reside, and the head of the chain (hash of the latest block). You can
then retrieve blocks by their indices, or iterate.

.. code-block::  python

    chain = Chain(store, head='48e399de59796ab1')
    first_block = chain[0]
    first_block.payload  # b'This is the first block!'

    for block in chain:
        print(block.index)  # will print 1, and then 0

You can also get the latest view of a current chain while building in ``block_builder.chain``.

Tree
~~~~

Similarly, to get a view of a tree, you need to specify the storage, and the
root of the tree (hash of the root node). You can then retrieve stored values
by corresponding lookup keys.

.. code-block::  python

    from hippepug.tree import Tree

    tree = Tree(store, root='150cc8da6d6cfa17')
    tree['foo']  # b'bar'
    'baz' in tree  # True


.. _proofs:

Producing and verifying proofs
------------------------------

When the creator of a data structure and the querier use the same storage
(e.g., external database), no additional work needs to be done. This scenario,
however, is not always possible. In such case, ``hippiepug`` allows to
explictly produce and verify proofs.


Chain
~~~~~

You can get the proof of block inclusion from a chain view:

.. code-block::  python

    block, proof = chain.get_block_by_index(0, return_proof=True)

Proof is just a set of blocks between head block and the request block (in
this case zero).

To verify the proof, the querier needs to locally reproduce a store
populating it with the blocks in the proof, and then query normally the chain
in the reproduced store. This can be done using a utility
:py:func:`hippiepug.chain.verify_chain_inclusion_proof`.

.. code-block:: python

    from hippiepug.chain import verify_chain_inclusion_proof

    verification_store = Sha256DictStore()
    verify_chain_inclusion_proof(verification_store,
                                 chain.head, block, proof)  # True.


Tree
~~~~

You can get the proof of value and lookup key inclusion from a tree view:

.. code-block::  python

    value, proof = tree.get_value_by_lookup_key('foo', return_proof=True)
    path, closure = proof

For trees, the proof is split for convenience into a tuple of two lists:
``path`` – list of nodes on the path from root to the leaf containing the
lookup key, and ``closure`` – list of other nodes that need to be known to
verify hashes of the tree root.

The mechanism of verifying an explicit proof is the same as with chains:
locally reproduce a store populating it with all the nodes in the proof,
and then query normally the tree in the reproduced store. This can be done
using a utility :py:func:`hippiepug.tree.verify_tree_inclusion_proof`.

.. code-block:: python

    from hippiepug.tree import verify_tree_inclusion_proof

    verification_store = Sha256DictStore()
    verify_tree_inclusion_proof(verification_store, tree.head,
                                lookup_key='foo', value=b'bar',
                                proof=proof)  # True.


Serialization
-------------

``hippiepug`` includes default binary serialization using ``msgpack`` library.

.. code-block::  python

    from hippiepug.pack import decode, encode

    block = chain[0]
    decode(encode(block)) == block  # True

If you want to define custom serializers, be sure to check the documentation of
:py:mod:`hippiepug.pack`. You need to be careful with custom encoders
to not jeopardize security of the data structure.

Once you have defined custom encoder and decoder, you can set them to global
defaults like this:

.. code-block::  python

    from hippiepug.pack import EncodingParams

    my_params = EncodingParams()
    my_params.encoder = lambda obj: b'encoded!'
    my_params.decoder = lambda encoded: b'decoded!'

    EncodingParams.set_global_default(my_params)

You can also limit the usage to specific context:

.. code-block::  python

    with my_params.as_default():
        encode(b'stub')  # b'encoded!'
