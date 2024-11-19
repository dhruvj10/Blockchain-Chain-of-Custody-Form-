from blockchain import Blockchain
import binascii
from datetime import datetime  # Add this import

def run():
    blockchain = Blockchain()
    password = input("Enter password (or press Enter to view encrypted values): ").strip()
    
    for i, block in enumerate(blockchain.blocks):
        print(f"\nBlock {i}:")
        values = block.get_decrypted_values(password)
        
        # Display timestamp in human-readable format
        timestamp = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Timestamp: {timestamp}")
        print(f"Previous Hash: {binascii.hexlify(block.prev_hash).decode()}")
        print(f"Case ID: {values['case_id']}")
        print(f"Evidence ID: {values['evidence_id']}")
        
        # Decode and display text fields, stripping null bytes
        try:
            state = block.state.decode('utf-8').rstrip('\0')
        except UnicodeDecodeError:
            state = binascii.hexlify(block.state).decode()
        print(f"State: {state}")
        
        try:
            creator = block.creator.decode('utf-8').rstrip('\0')
        except UnicodeDecodeError:
            creator = binascii.hexlify(block.creator).decode()
        print(f"Creator: {creator}")
        
        try:
            owner = block.owner.decode('utf-8').rstrip('\0')
        except UnicodeDecodeError:
            owner = binascii.hexlify(block.owner).decode()
        print(f"Owner: {owner}")
        
        try:
            data = block.data.decode('utf-8').rstrip('\0')
        except UnicodeDecodeError:
            data = binascii.hexlify(block.data).decode()
        print(f"Data: {data}")