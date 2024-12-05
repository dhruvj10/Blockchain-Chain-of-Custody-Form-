import argparse
import os
from blockchain import Blockchain
from datetime import datetime
from utils import get_role_passwords, validate_password

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
        creator_password = get_role_passwords()['creator']  # Get creator password
        
        for block in blockchain.blocks:
            # Skip genesis block
            if block.state == b"INITIAL\0\0\0\0\0":
                continue
                
            print(f"prev_hash:\t{block.prev_hash}\ntimestamp:\t{block.timestamp}\ncase_id:\t{block.case_id}\nevidence_id:\t{block.evidence_id}\nstate:\t\t{block.state}\ncreator:\t{block.creator}\nowner:\t\t{block.owner}\ndata:\t\t{block.data}\n")

            # Decrypt and check if this block matches our item_id
            decrypted_values = block.get_decrypted_values(creator_password)
            if int(decrypted_values['evidence_id']) == int(item_id):
                found_entries = True
                # Format the output
                timestamp = format_timestamp(block.timestamp)
                state = block.state
                creator = block.creator
                
                # Print entry details
                print(f"State: {state}")
                print(f"Time of action: {timestamp}")
                if creator:
                    print(f"Creator/Owner: {creator}")
                if block.data:
                    print("Additional data: " + block.data.decode().rstrip('\x00'))
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