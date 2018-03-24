import pytest

from hippiepug.store import Sha256DictStore
from hippiepug.struct import ChainBlock, TreeNode, TreeLeaf


@pytest.fixture
def object_store():
    return Sha256DictStore()


@pytest.fixture
def block():
    return ChainBlock(payload='Test payload')


@pytest.fixture
def node():
    return TreeNode(pivot_prefix='test')


@pytest.fixture
def leaf():
    return TreeLeaf(lookup_key='test')
