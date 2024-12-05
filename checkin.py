import argparse
import datetime
import sys
from block import Block
from blockchain import Blockchain
import os
from utils import validate_password, get_role_passwords, get_owner

def parse_checkin_args(args):
    parser = argparse.ArgumentParser(description='Checkin evidence items to the blockchain')
    parser.add_argument('-i', '--item_id', required=True, type=int, help='Evidence item identifier')
    parser.add_argument('-p', '--password', required=True, help='Password of the owner')
    return parser.parse_args(args)

def find_evidence_item(blockchain, item_id):
    creator_password = get_role_passwords()['creator']  # Get creator password
    latest_block = None
    
    # Skip genesis block and look for the most recent state of the item
    for block in blockchain.blocks[1:]:
        decrypted_values = block.get_decrypted_values(creator_password)  # Use creator password
        if decrypted_values.get('evidence_id') == item_id:
            latest_block = block
    return latest_block

def run():
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    args = parse_checkin_args(sys.argv[2:])
    
    # Validate password
    if not validate_password(args.password):
        print("Error: Invalid password", file=sys.stderr)
        sys.exit(1)
    
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
    
    # Check if item is already checked in
    if existing_block.state.rstrip(b'\0') == b"CHECKEDIN":
        print(f"Error: Evidence item {args.item_id} is already checked in", file=sys.stderr)
        sys.exit(1)

    # Check if item is already removed in
    if existing_block.state.rstrip(b'\0') in [b'DESTROYED', b'REMOVED', b'DISPOSED', b'RELEASED']:
        print(f"Error: Evidence item {args.item_id} has been removed", file=sys.stderr)
        sys.exit(1)
    
    # Get case ID from existing block
    creator_password = get_role_passwords()['creator']  # Get creator password
    decrypted_values = existing_block.get_decrypted_values(creator_password)  # Use creator password
    case_id = decrypted_values['case_id']
    
    owner = get_owner(args.password)

    # Create new checkin block
    block = Block(
        case_id=case_id,
        evidence_id=args.item_id,
        state=b"CHECKEDIN",
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
    print(f"Checked in item: {args.item_id}")
    print(f"Status: CHECKEDIN")
    print(f"Time of action: {timestamp}")