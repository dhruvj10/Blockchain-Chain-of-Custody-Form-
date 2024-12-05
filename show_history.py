import argparse
import os
from blockchain import Blockchain
from datetime import datetime
from utils import get_role_passwords, validate_password

def parse_history_args(args):
    parser = argparse.ArgumentParser(description='Show history of evidence items')
    parser.add_argument('-i', '--item_id', required=True, help='Evidence item identifier')
    parser.add_argument('-p', '--password', required=True, help='Password for authentication')
    parser.add_argument('-r', '--reverse', action='store_true', help='Display history in reverse order')
    return parser.parse_args(args)

def format_timestamp(timestamp):
    # Convert timestamp to ISO format with Z suffix
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def show_item_history(item_id, password, reverse=False):
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
        found_entries = []
        creator_password = get_role_passwords()['creator']  # Get creator password
        
        for block in blockchain.blocks:
            # Skip genesis block
            if block.state == b"INITIAL\0\0\0\0\0":
                continue
                
            # Decrypt and check if this block matches our item_id
            decrypted_values = block.get_decrypted_values(creator_password)
            if int(decrypted_values['evidence_id']) == int(item_id):
                # Format the output
                timestamp = format_timestamp(block.timestamp)
                state = block.state
                creator = block.creator
                
                # Collect entry details
                entry = {
                    'State': state,
                    'Time of action': timestamp,
                    'Creator/Owner': creator,
                    'Additional data': block.data.decode().rstrip('\x00') if block.data else None
                }
                found_entries.append(entry)
        
        # Reverse the order if the reverse flag is set
        if reverse:
            found_entries.reverse()
        
        # Print entries
        for entry in found_entries:
            print(f"State: {entry['State']}")
            print(f"Time of action: {entry['Time of action']}")
            if entry['Creator/Owner']:
                print(f"Creator/Owner: {entry['Creator/Owner']}")
            if entry['Additional data']:
                print("Additional data: " + entry['Additional data'])
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
    show_item_history(args.item_id, args.password, args.reverse)

if __name__ == "__main__":
    run()