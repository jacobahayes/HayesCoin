from flask import Flask
from flask import request
import hashlib
import datetime
import json
import uuid
import requests


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
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


# This node and its transaction list
node = Flask(__name__)
# random ID/address for owner of this node
miner_addr = str(uuid.uuid4())
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


@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain_to_send = blockchain
    # Make blocks dictionaries in order to send as JSON objects later
    for block in chain_to_send:
        block = {
            'index': str(block.index),
            'timestamp': str(block.timestamp),
            'data': str(block_data),
            'hash': block.hash
        }
    return json.dumps(chain_to_send)


# Get the peer nodes' blockchains
def find_chains():
    other_chains = []
    for url in peer_nodes:
        chain = requests.get(url + '/blocks').content
        # convert JSON to python dict
        chain = json.loads(chain)
        other_chains.append(chain)

    return other_chains


# Consensus algorithm is the standard: longest chain
def consensus():
    other_chains = find_chains()
    longest_chain = blockchain
    for chain in other_chains:
        if len(chain) > len(longest_chain):
            longest_chain = chain

    blockchain = longest_chain


# Proof of work algorithm will increment a guess until a node finds a number divisible by 7 and the proof of work for
#  the previous block
def proof_of_work(prev_proof):
    guess = prev_proof + 1
    while not (guess % 7 == 0 and guess % prev_proof == 0):
        guess += 1
    return guess


@node.route('/mine', methods=['GET'])
def mine():
    prev_block = blockchain[len(blockchain) - 1]
    prev_proof = prev_block.data['proof-of-work']
    # Will hang here until a new proof is found
    proof = proof_of_work(prev_proof)

    node_transactions.append({
        'sender': 'network',
        'recipient': miner_addr,
        'amount': 1
    })

    mined_block_data = {
        'proof-of-work': proof,
        'transactions': node_transactions
    }
    mined_block_index = prev_block.index + 1
    mined_block = Block(mined_block_index, datetime.datetime.now(), mined_block_data, prev_block.hash)
    blockchain.append(mined_block)

    return json.dumps({
        'index': mined_block.index,
        'timestamp': str(mined_block.timestamp),
        'data': mined_block_data,
        'previous_hash': mined_block.previous_hash,
        'hash': mined_block.hash
    })


# Takes in the last block in the chain as a parameter in order to add the next one onto the chain
def new_block(prev_block):
    new_index = prev_block.index + 1
    new_timestamp = datetime.datetime.now()
    new_data = "Block: " + str(new_index)
    return Block(new_index, new_timestamp, new_data, prev_block.hash)


node.run()
