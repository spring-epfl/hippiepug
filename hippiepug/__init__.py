__version__ = '0.4.2'
__title__ = 'hippiepug'
__author__ = 'Bogdan Kulynych'
__email__ = 'hello@bogdankulynych.me'
__copyright__ = '2018 by Bogdan Kulynych (EPFL SPRING Lab)'
__description__ = 'Sublinear-lookup blockchains and efficient key-value Merkle trees with a flexible storage backend'
__url__ = 'https://github.com/spring-epfl/hippiepug'
__license__ = 'MIT'


from .chain import BlockBuilder, Chain
from .tree import TreeBuilder, Tree
from .pack import EncodingParams, encode, decode
