import pytest
import math
import six

from mock import MagicMock

from hippiepug.struct import ChainBlock
from hippiepug.chain import Chain, BlockBuilder
from hippiepug.store import IntegrityValidationError
from hippiepug.pack import encode, decode


CHAIN_SIZES = [1, 2, 3, 10, 42]


@pytest.fixture
def chain(object_store):
    return Chain(object_store)


@pytest.fixture
def block_builder(chain):
    return BlockBuilder(chain)


@pytest.fixture(params=CHAIN_SIZES)
def chain_and_hashes(request, block_builder):
    hashes = []
    for i in range(request.param):
        block_builder.payload = 'Block {}'.format(i)
        block_builder.commit()
        hashes.append(block_builder.chain.head)
    return block_builder.chain, hashes


def test_block_hash_value(block_builder):
    """Check that after commiting the chain head is hash of the block."""
    chain = block_builder.chain
    assert chain.head is None

    block = block_builder.commit()
    block_hash = chain.object_store.hash_object(encode(block))
    assert chain.head == block_hash


def test_builder_skipchain_fingers(chain_and_hashes):
    """Check that skipchain fingers are correct."""
    chain, hashes = chain_and_hashes
    n = chain.head_block.index + 1

    block_builder = BlockBuilder(chain)
    assert block_builder.index == n

    fingers = block_builder.fingers
    finger_indices = [i for (i, h) in fingers]
    upper_bound_num_fingers = math.floor(math.log(n, 2)) + 1
    assert 1 <= len(fingers) <= upper_bound_num_fingers


@pytest.mark.parametrize('chain_size', CHAIN_SIZES)
def test_builder_commit_blocks(block_builder, chain_size):
    """Commit couple of blocks and check that the chain head moves."""
    expected_head = None
    for i in range(chain_size):
        assert block_builder.chain.head == expected_head
        block_builder.payload = 'Block {}'.format(i)
        block = block_builder.commit()
        expected_head = block_builder.chain.object_store.hash_object(
                encode(block))


def test_empty_chain(object_store):
    """Check that empty chain raises only the expected error."""
    chain = Chain(object_store)
    assert chain.head is None
    assert chain.get_block_by_index(0) is None


def test_chain_get_block_by_hash_from_cache(chain_and_hashes):
    """Check that blocks are retrievable by hashes from cache."""
    chain, hashes = chain_and_hashes
    chain._cache = MagicMock()
    chain._cache.__contains__.return_value = True
    for i, block_hash in enumerate(hashes):
        block = chain._get_block_by_hash(block_hash)
        chain._cache.__getitem__.assert_called_with(block_hash)
    return block


def test_chain_get_block_by_hash_from_store(chain_and_hashes):
    """Check that blocks are retrievable by hashes with cache cleared."""
    chain, hashes = chain_and_hashes
    for i, block_hash in enumerate(hashes):
        chain._cache.clear()
        block = chain._get_block_by_hash(block_hash)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_chain_get_block_by_hash_fails_if_hash_wrong(chain_and_hashes):
    """Check that exception is raised if the hash is incorrect."""
    chain, hashes = chain_and_hashes
    chain._cache.clear()
    target_hash = hashes[0]

    substitute_block = ChainBlock(payload='Hacked!')
    chain.object_store._backend[target_hash] = encode(substitute_block)

    with pytest.raises(IntegrityValidationError):
        chain._get_block_by_hash(target_hash)


def test_chain_get_block_by_hash_fails_if_not_block(chain_and_hashes):
    """Check that exception is raised if the hash is incorrect."""
    chain, hashes = chain_and_hashes
    extra_obj_hash = chain.object_store.add(b'extra')
    with pytest.raises(ValueError):
        chain._get_block_by_hash(extra_obj_hash)


def test_chain_get_block_by_index_from_cache(chain_and_hashes):
    """Check that blocks are retrievable by index from cache."""
    chain, hashes = chain_and_hashes
    cache_copy = chain._cache.copy()

    chain._cache = MagicMock()
    chain._cache.__contains__.return_value = True

    def mock_getitem(k):
        return cache_copy[k]

    chain._cache.__getitem__.side_effect = mock_getitem

    for i, block_hash in enumerate(hashes):
        a = chain.get_block_by_index(i)
        chain._cache.__getitem__.assert_called_with(block_hash)


def test_get_block_by_index_from_store(chain_and_hashes):
    """Check that blocks are retrievable by index from cache."""
    chain, hashes = chain_and_hashes
    for i, _ in enumerate(hashes):
        chain._cache.clear()
        block = chain.get_block_by_index(i)
        assert block.payload == 'Block {}'.format(i)
    return block


def test_chain_get_block_by_index_fails_if_out_of_range(chain_and_hashes):
    """Check that exception is thrown if the index out of range."""
    chain, hashes = chain_and_hashes
    n = chain.head_block.index
    with pytest.raises(IndexError):
        chain.get_block_by_index(-1)
    with pytest.raises(IndexError):
        chain.get_block_by_index(n+1)


def test_chain_iterator(chain_and_hashes):
    """Check the iterator."""
    chain, hashes = chain_and_hashes
    for block, expected_block_hash in zip(chain, reversed(hashes)):
        block_hash = chain.object_store.hash_object(encode(block))
        assert block_hash == expected_block_hash


def test_chain_proof(object_store):
    """Check returned inclusion proof."""
    chain1 = Chain(object_store)
    for i in range(10):
        block_builder = BlockBuilder(chain1)
        block_builder.payload='Block %i' % i
        block_builder.commit()

    result, proof = chain1.get_block_by_index(2, return_proof=True)
    proof_store = chain1.object_store.__class__()

    for block in proof:
        serialized_block = encode(block)
        proof_store.add(serialized_block)

    chain2 = Chain(proof_store, head=chain1.head)
    assert chain2.get_block_by_index(2).payload == 'Block 2'

