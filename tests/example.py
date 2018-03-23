from hippiepug.chain import Chain, BlockBuilder
from hippiepug.store import Sha256DictStore
from hippiepug.pack import decode


store = Sha256DictStore()
chain = Chain(store)

block_builder = BlockBuilder(chain)
block_builder.payload = 'Hello, world!'
block = block_builder.commit()

assert decode(store.get(chain.head)) == block
