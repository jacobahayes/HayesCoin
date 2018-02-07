import datetime
import hashlib


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash()

    def hash(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode())
        return sha.hexdigest()


# Manually creates a genesis block to start the block chain
# Naturally, the index is 0. Previous hash is arbitrary
def genesis_block():
    return Block(0, datetime.datetime.now(), "Genesis", "1776")


# Takes in the last block in the chain as a parameter in order to add the next one onto the chain
def new_block(prev_block):
    new_index = prev_block.index + 1
    new_timestamp = datetime.datetime.now()
    new_data = "Block: " + str(new_index)
    return Block(new_index, new_timestamp, new_data, prev_block.hash)


# Test: create a blockchain with a genesis block, then add an arbitrary number of blocks to the chain
blockchain = [genesis_block()]
previous_block = blockchain[0]
chain_length = 10

for i in range(0, chain_length):
    next_block = new_block(previous_block)
    blockchain.append(next_block)
    previous_block = next_block
    print(next_block.data + " has been added to the blockchain at " + str(next_block.timestamp))
    print("Hash: " + str(next_block.hash))
