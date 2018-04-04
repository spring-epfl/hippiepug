__version__ = '0.1.2'
__title__ = 'hippiepug'
__author__ = 'Bogdan Kulynych'
__email__ = 'hello@bogdankulynych.me'
__copyright__ = 'Copyright (c) 2018 Bogdan Kulynych, EPFL SPRING Lab'
__description__ = 'Sublinear-lookup blockchains and efficient key-value Merkle trees with a flexible storage backend'
__url__ = 'https://github.com/spring-epfl/hippiepug'
__license__ = 'AGPLv3+'


from .chain import BlockBuilder, Chain
from .tree import TreeBuilder, Tree
from .pack import EncodingParams, encode, decode
