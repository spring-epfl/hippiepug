from hippiepug.chain import MsgpackBlock, Chain


chain = Chain(MsgpackBlock)

block = chain.make_next_block()
block.payload = 'Hello, world!'
block.commit()

assert chain.head == block.hash_value

