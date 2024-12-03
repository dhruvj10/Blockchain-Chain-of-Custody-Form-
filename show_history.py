import argparse
import os
from blockchain import Blockchain
from datetime import datetime

def parse_history_args(args):
    parser = argparse.ArgumentParser(description='Show history of evidence items')
    parser.add_argument('-i', '--item_id', required=True, help='Evidence item identifier')
    parser.add_argument('-p', '--password', required=True, help='Password for authentication')
    return parser.parse_args(args)

def format_timestamp(timestamp):
    # Convert timestamp to ISO format with Z suffix
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def show_item_history(item_id, password):
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)
    
    try:
        # Load the blockchain
        blockchain = Blockchain(blockchain_file)
        
        # Find all entries for the specified item_id
        found_entries = False
        for block in blockchain.blocks:
            # Skip genesis block
            if block.state == b"INITIAL\0\0\0\0\0":
                continue
                
            # Decrypt and check if this block matches our item_id
            decrypted_values = block.get_decrypted_values(password)
            if decrypted_values['evidence_id'] == str(item_id):
                found_entries = True
                # Format the output
                timestamp = format_timestamp(block.timestamp)
                state = block.state.rstrip(b'\x00').decode()
                creator = block.creator.rstrip(b'\x00').decode()
                
                # Print entry details
                print(f"State: {state}")
                print(f"Time of action: {timestamp}")
                if creator:
                    print(f"Creator/Owner: {creator}")
                if block.data:
                    print(f"Additional data: {block.data.decode().rstrip('\x00')}")
                print()  # Empty line between entries
        
        if not found_entries:
            print(f"No history found for evidence item: {item_id}")
            exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

def run():
    import sys
    args = parse_history_args(sys.argv[2:])  # Skip the first two arguments (script name and command)
    show_item_history(args.item_id, args.password)

if __name__ == "__main__":
    run()