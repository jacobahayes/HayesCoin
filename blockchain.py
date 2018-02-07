from flask import Flask
from flask import request
import hashlib
import datetime
import json
import uuid


# This node and its transaction list
node = Flask(__name__)

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
# Naturally, the index is 0. Proof of work and the previous hash is arbitrary
def genesis_block():
    return Block(0, datetime.datetime.now(), {
        'proof-of-work': 1788,
        'transactions': None
    }, '1776')


# random ID/address for owner of this node
miner_addr = uuid.uuid4()
# this node's copy of the block chain
blockchain = [genesis_block()]
# this node's transaction and peer lists
node_transactions = []
peer_nodes = []


@node.route('/transaction', methods=['POST'])
def transaction():
    if request.method == 'POST':
        # Get transaction data for any POST  request and add transaction to the list
        new_transaction = request.get_json()
        node_transactions.append(new_transaction)

        # Log transaction data in the console
        print('New transaction')
        print('Sender: ' + new_transaction['sender'])
        print('Recipient: ' + new_transaction['recipient'])
        print('Amount: ' + new_transaction['amount'])

        return 'Successful transaction submission\n'


# Proof of work algorithm will increment a guess until a node finds a number divisible by 7 and the proof of work for
#  the previous block
def proof_of_work(last_proof):
    guess = last_proof + 1
    while not (guess % 7 == 0 and guess % last_proof == 0):
        guess += 1
    return guess


# Takes in the last block in the chain as a parameter in order to add the next one onto the chain
def new_block(prev_block):
    new_index = prev_block.index + 1
    new_timestamp = datetime.datetime.now()
    new_data = "Block: " + str(new_index)
    return Block(new_index, new_timestamp, new_data, prev_block.hash)

node.run()
