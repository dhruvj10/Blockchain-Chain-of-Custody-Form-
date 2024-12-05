import argparse
import datetime
import sys
from block import Block
from blockchain import Blockchain
import os
from utils import get_role_passwords, validate_password, get_owner

def parse_checkout_args(args):
    parser = argparse.ArgumentParser(description='Checkout evidence items from the blockchain')
    parser.add_argument('-i', '--item_id', required=True, type=int, help='Evidence item identifier')
    parser.add_argument('-p', '--password', required=True, help='Password of the owner')
    return parser.parse_args(args)

def find_evidence_item(blockchain, item_id):
    creator_password = get_role_passwords()['creator']  # Get creator password
    latest_block = None
    
    # Skip genesis block and look for the most recent state of the item
    for block in blockchain.blocks[1:]:
        print(creator_password)
        decrypted_values = block.get_decrypted_values(creator_password)  # Use creator password
        print(decrypted_values)
        print(f"\nSearching block - Decrypted values: {decrypted_values}")
        if decrypted_values.get('evidence_id') is not None:
            print(f"Comparing {decrypted_values['evidence_id']} with {item_id}")
            if decrypted_values['evidence_id'] == item_id:
                latest_block = block
    return latest_block

def run():
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    args = parse_checkout_args(sys.argv[2:])
    
    # Load blockchain
    blockchain = Blockchain(blockchain_file)
    if not blockchain.blocks:
        print("Error: Blockchain is empty", file=sys.stderr)
        sys.exit(1)
    
    # Find the evidence item
    existing_block = find_evidence_item(blockchain, args.item_id)
    if not existing_block:
        print(f"Error: Evidence item {args.item_id} not found", file=sys.stderr)
        sys.exit(1)
    
    # Check if item is already checked out
    if existing_block.state.rstrip(b'\0') == b"CHECKEDOUT":
        print(f"Error: Evidence item {args.item_id} is already checked out", file=sys.stderr)
        sys.exit(1)
    
    # Validate owner password
    if not validate_password(args.password):
        print("Error: Invalid password", file=sys.stderr)
        sys.exit(1)
    
    # Any valid password can checkout
    
    # Get case ID from existing block
    creator_password = get_role_passwords()['creator']  # Get creator password
    decrypted_values = existing_block.get_decrypted_values(creator_password)  # Use creator password
    case_id = decrypted_values['case_id']
    
    owner = get_owner(args.password)

    # Create new checkout block
    block = Block(
        prev_hash=bytes(32),
        case_id=case_id,
        evidence_id=args.item_id,
        state=b"CHECKEDOUT",
        creator=existing_block.creator,
        owner=owner,
        data=b""
    )
    
    # Add block to blockchain
    blockchain.add_block(block)
    
    # Get current time in ISO format with Z suffix
    timestamp = datetime.datetime.now().isoformat() + "Z"
    
    # Print output in the expected format
    print(f"Case: {case_id}")
    print(f"Checked out item: {args.item_id}")
    print(f"Status: CHECKEDOUT")
    print(f"Time of action: {timestamp}")