from blockchain import Blockchain
from block import Block

def run():
    blockchain = Blockchain()
    result = blockchain.init_blockchain()
    if result:
        print("Genesis block created successfully")
    else:
        print("Blockchain already initialized")