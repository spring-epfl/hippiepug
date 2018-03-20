import pytest
import six

from hippiepug.chain import MsgpackBlock, Chain
from hippiepug.store import DictStore, IntegrityValidationError
from hippiepug import utils


CHAIN_SIZES = [1, 2, 3, 10]


@pytest.fixture
def object_store():
    return DictStore()


@pytest.fixture
def block():
    return MsgpackBlock(payload='Test payload')


@pytest.fixture
def chain_factory(object_store, block):
    class ChainFactory:
        def make(self, block_cls=block.__class__):
            return Chain(block_cls, object_store)
    yield ChainFactory()


@pytest.fixture
def chain(object_store, block):
    return Chain(block_cls=block.__class__, object_store=object_store)


@pytest.fixture(params=CHAIN_SIZES)
def chain_and_hashes(request, chain_factory):
    chain = chain_factory.make(block_cls=MsgpackBlock)
    hashes = []
    for i in range(request.param):
        block = chain.make_next_block()
        block.payload = 'Block {}'.format(i)
        block.commit()
        hashes.append(block.hash_value)
    return chain, hashes


def test_block_hash_value(chain):
    """Check that block.hash_value is a hash of a serialized block."""
    block = chain.make_next_block()
    assert block.hash_value is None
    block.commit()
    assert block.hash_value == chain.object_store.hash_object(
            block.serialize())


def test_block_serialization(block):
    """Test if a block serializes fine."""
    a = block
    serialized = a.serialize()
    b = block.deserialize(serialized)
    assert a.index == b.index \
        and a.fingers == b.fingers \
        and a.payload == b.payload


def test_block_repr(block):
    """Check if repr returns a string with block class name."""
    assert block.__class__.__name__ in repr(block)


def test_chain_repr(chain_factory):
    """Check if repr returns a string with chain class name."""
    chain = chain_factory.make()
    assert 'Chain(' in repr(chain)


def test_make_next_block_doesnt_change_chain(chain):
    """
    chain.make_next_block() should not modify the chain before
    the block is commited.
    """
    assert chain.head is None
    block = chain.make_next_block()
    assert chain.head is None


def test_chain_commit_blocks(chain):
    """
    Commit couple of blocks and check that the chain head
    moves.
    """
    expected_head = None
    for i in range(5):
        assert chain.head == expected_head
        block = chain.make_next_block()
        block.payload = 'Block {}'.format(i)
        block.commit()
        expected_head = block.hash_value


def test_commit_fails_if_chain_undefined(block):
    """
    Commiting the block should fail if no chain is associated.
    """
    with pytest.raises(ValueError):
        block.commit()


def test_get_block_by_hash_from_cache(chain_and_hashes):
    """
    Check that blocks are retrievable by hashes from cache.
    """
    chain, hashes = chain_and_hashes
    for i, block_hash in enumerate(hashes):
        block = chain.get_block_by_hash(block_hash)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_hid_from_store(chain_and_hashes):
    """
    Check that blocks are retrievable by hashes with cache cleared.
    """
    chain, hashes = chain_and_hashes
    for i, block_hash in enumerate(hashes):
        chain._cache.clear()
        block = chain.get_block_by_hash(block_hash)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_hash_fails_if_hash_wrong(chain_and_hashes):
    """
    Check that exception is raised if the hash is incorrect.
    """
    chain, hashes = chain_and_hashes
    chain._cache.clear()
    target_hash = hashes[0]

    substitute_block = MsgpackBlock(payload='Hacked!')
    chain.object_store._backend[target_hash] = substitute_block.serialize()

    with pytest.raises(IntegrityValidationError):
        chain.get_block_by_hash(target_hash)


def test_get_block_by_index_from_cache(chain_and_hashes):
    """
    Check that blocks are retrievable by index from cache.
    """
    chain, hashes = chain_and_hashes
    for i, _ in enumerate(hashes):
        a = chain.get_block_by_index(i)
        assert a.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_index_from_store(chain_and_hashes):
    """
    Check that blocks are retrievable by index from cache
    """
    chain, hashes = chain_and_hashes
    for i, _ in enumerate(hashes):
        chain._cache.clear()
        block = chain.get_block_by_index(i)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_index_fails_if_block_out_of_range(chain_and_hashes):
    """Check that exception is thrown if the index out of range. """
    chain, hashes = chain_and_hashes
    n = chain.head_block.index
    with pytest.raises(IndexError):
        chain.get_block_by_index(-1)
    with pytest.raises(IndexError):
        chain.get_block_by_index(n+1)


def test_chain_iterator(chain_and_hashes):
    """Check the iterator."""
    chain, hashes = chain_and_hashes
    for block, block_hash in zip(chain, reversed(hashes)):
        assert block.hash_value == block_hash


def test_chain_evidence(chain_factory, object_store):
    """Check returned evidence."""
    chain1 = chain_factory.make(block_cls=MsgpackBlock)
    for i in range(10):
        block = chain1.make_next_block(payload='Block %i' % i)
        block.commit()

    res, evidence = chain1.get_block_by_index(2, return_evidence=True)
    serialized_evidence = {block.hash_value: block.serialize()
                           for block in evidence}

    chain2 = chain_factory.make(block_cls=MsgpackBlock)
    chain2.head = chain1.head
    chain2.object_store = DictStore(serialized_evidence)
    assert chain2.get_block_by_index(2).payload == 'Block 2'
