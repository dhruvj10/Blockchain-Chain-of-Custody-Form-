import os
import struct  # Add this import
from block import Block

class Blockchain:
    def __init__(self, filename="blockchain.bin"):
        self.filename = filename
        self.blocks = []
        self.load_blockchain()

    def load_blockchain(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                while True:
                    try:
                        fixed_size = struct.calcsize(Block.FORMAT)
                        fixed_data = f.read(fixed_size)
                        if not fixed_data:
                            break
                        
                        data_length = struct.unpack(Block.FORMAT, fixed_data)[7]
                        var_data = f.read(data_length)
                        
                        block = Block.deserialize(fixed_data + var_data)
                        self.blocks.append(block)
                    except:
                        break

    def init_blockchain(self):
        if not self.blocks:
            genesis_block = Block.create_initial_block()
            self.blocks.append(genesis_block)
            self.save_blockchain()
            return True
        return False

    def save_blockchain(self):
        with open(self.filename, 'wb') as f:
            for block in self.blocks:
                f.write(block.serialize())

    def add_block(self, block):
        if self.blocks:
            block.prev_hash = self.blocks[-1].calculate_hash()
        self.blocks.append(block)
        self.save_blockchain()