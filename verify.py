import os
from blockchain import Blockchain

def verify_blockchain():
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)
    
    try:
        # Load the blockchain
        blockchain = Blockchain(blockchain_file)
        
        # Check if blockchain is empty
        if len(blockchain.blocks) == 0:
            print("Error: blockchain is empty")
            exit(1)
        
        # Verify the initial block (genesis block)
        genesis_block = blockchain.blocks[0]
        if (genesis_block.prev_hash != bytes(32) or
            genesis_block.timestamp != 0 or
            genesis_block.case_id != b"0" * 32 or
            genesis_block.evidence_id != b"0" * 32 or
            genesis_block.state != b"INITIAL\0\0\0\0\0" or
            genesis_block.creator != b"\0" * 12 or
            genesis_block.owner != b"\0" * 12 or
            genesis_block.data != b"Initial block\0" or
            genesis_block.data_length != 14):
            print("Error: invalid genesis block")
            exit(1)
        
        # Verify chain of hashes and block integrity
        for i in range(1, len(blockchain.blocks)):
            current_block = blockchain.blocks[i]
            previous_block = blockchain.blocks[i-1]
            
            # Verify previous hash matches
            if current_block.prev_hash != previous_block.calculate_hash():
                print(f"Error: invalid hash chain at block {i}")
                exit(1)
            
            # Verify block state is valid
            if current_block.state not in [b"CHECKEDIN\x00\x00", b"INITIAL\0\0\0\0\0"]:
                print(f"Error: invalid state at block {i}")
                exit(1)
            
            # Verify fixed-length fields
            if (len(current_block.creator) != 12 or
                len(current_block.owner) != 12 or
                len(current_block.state) != 12):
                print(f"Error: invalid field length at block {i}")
                exit(1)
            
            # Verify data length matches actual data
            if len(current_block.data) != current_block.data_length:
                print(f"Error: invalid data length at block {i}")
                exit(1)
        
        # If we get here, all verifications passed
        print("Blockchain verification passed")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

def run():
    verify_blockchain()

if __name__ == "__main__":
    run()