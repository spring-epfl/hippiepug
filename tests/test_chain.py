import pytest
import six

from hippiepug.chain import BaseBlock, Chain
from hippiepug.store import MemoryStore
from hippiepug import utils


CHAIN_SIZES = [1, 2, 3, 10]


@pytest.fixture
def object_store():
    return MemoryStore()


@pytest.fixture
def block():
    return BaseBlock(payload='Test payload')


@pytest.fixture
def chain_factory(object_store):
    class ChainFactory:
        def make(self, block_cls=BaseBlock):
            return Chain(block_cls, object_store)
    yield ChainFactory()


@pytest.fixture(params=CHAIN_SIZES)
def chain_and_hids(request, chain_factory):
    chain = chain_factory.make(block_cls=BaseBlock)
    hids = []
    for i in range(request.param):
        block = chain.make_next_block()
        block.payload = 'Block {}'.format(i)
        block.commit()
        hids.append(block.hid)
    return chain, hids


def test_default_serialization(block):
    """
    Test if BaseBlock serializes fine.
    """
    a = block
    serialized = a.serialize()
    b = BaseBlock.deserialize(serialized)
    assert a.index == b.index \
        and a.fingers == b.fingers \
        and a.payload == b.payload


def test_block_hid(block):
    """
    Check that block.hid is a hash of a serialized block.
    """
    assert block.hid == utils.ascii_hash(block.serialize())


def test_block_repr(block):
    assert 'BaseBlock(' in repr(block)


def test_chain_repr(chain_factory):
    chain = chain_factory.make()
    assert 'Chain(' in repr(chain)


def test_make_next_block_doesnt_change_chain(chain_factory):
    """
    chain.make_next_block() should not modify the chain before
    the block is commited.
    """
    chain = chain_factory.make()
    assert chain.head is None
    block = chain.make_next_block()
    assert chain.head is None


def test_append_blocks(chain_factory):
    """
    Commit couple of blocks and check that the chain head
    moves.
    """
    chain = chain_factory.make(block_cls=BaseBlock)
    expected_head = None

    for i in range(5):
        assert chain.head == expected_head
        block = chain.make_next_block()
        block.payload = 'Block {}'.format(i)
        block.commit()
        expected_head = block.hid


def test_commit_fails_if_chain_undefined():
    """
    Commiting the block should fail if no chain is associated.
    """
    block = BaseBlock()
    with pytest.raises(ValueError):
        block.commit()


def test_get_block_by_hid_from_cache(chain_and_hids):
    """
    Check that blocks are retrievable by hashes from cache.
    """
    chain, hids = chain_and_hids
    for i, hid in enumerate(hids):
        block = chain.get_block_by_hid(hid)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_hid_from_store(chain_and_hids):
    """
    Check that blocks are retrievable by hashes with cache cleared.
    """
    chain, hids = chain_and_hids
    for i, hid in enumerate(hids):
        chain._cache.clear()
        block = chain.get_block_by_hid(hid)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_hid_fails_if_hash_wrong(chain_and_hids):
    """
    Check that exception is raised if the hash is incorrect.
    """
    chain, hids = chain_and_hids
    chain._cache.clear()
    target_hid = hids[0]

    substitute_block = BaseBlock(payload='Hacked!')
    chain.object_store._backend[target_hid] = substitute_block.serialize()

    with pytest.raises(utils.IntegrityValidationError):
        chain.get_block_by_hid(target_hid)


def test_get_block_by_index_from_cache(chain_and_hids):
    """
    Check that blocks are retrievable by index from cache.
    """
    chain, hids = chain_and_hids
    for i, _ in enumerate(hids):
        a = chain.get_block_by_index(i)
        assert a.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_index_from_store(chain_and_hids):
    """
    Check that blocks are retrievable by index from cache
    """
    chain, hids = chain_and_hids
    for i, _ in enumerate(hids):
        chain._cache.clear()
        block = chain.get_block_by_index(i)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_get_block_by_index_fails_if_block_out_of_range(chain_and_hids):
    """
    Check that exception is thrown if the hash is incorrect.
    """
    chain, hids = chain_and_hids
    n = chain.head_block.index
    with pytest.raises(IndexError):
        chain.get_block_by_index(-1)
    with pytest.raises(IndexError):
        chain.get_block_by_index(n+1)

def test_chain_iterator(chain_and_hids):
    """
    Check the iterator.
    """
    chain, hids = chain_and_hids
    for block, hid in zip(chain, reversed(hids)):
        assert block.hid == hid


def test_chain_evidence(chain_factory, object_store):
    """
    Check returned evidence.
    """
    chain1 = chain_factory.make(block_cls=BaseBlock)
    for i in range(10):
        chain1.make_next_block(payload='Block %i' % i).commit()

    res, evidence = chain1.get_block_by_index(2, return_evidence=True)
    serialized_evidence = {block.hid: block.serialize()
                           for block in evidence}

    chain2 = chain_factory.make(block_cls=BaseBlock)
    chain2.head = chain1.head
    chain2.object_store = MemoryStore(serialized_evidence)
    assert chain2.get_block_by_index(2).payload == 'Block 2'
