import argparse
import uuid
import datetime
from block import Block
from blockchain import Blockchain
import os
import sys
from utils import get_role_passwords, validate_password

def parse_add_args(args):
    parser = argparse.ArgumentParser(description='Add evidence items to the blockchain')
    parser.add_argument('-c', '--case_id', required=True, help='Case identifier (UUID)')
    parser.add_argument('-i', '--item_ids', required=True, nargs='+', help='Evidence item identifier(s)')
    parser.add_argument('-g', '--creator', required=True, help='Creator of the evidence item')
    parser.add_argument('-p', '--password', required=True, help='Password for the creator')
    return parser.parse_args(args)

def validate_case_id(case_id):
    try:
        return str(uuid.UUID(case_id))
    except ValueError:
        print("Error: Invalid case ID format")
        exit(1)

def validate_evidence_ids(blockchain, evidence_ids):
    creator_password = get_role_passwords()['creator']
    existing_ids = set()
    
    # Skip the initial block (genesis block)
    for block in blockchain.blocks[1:]:
        decrypted_values = block.get_decrypted_values(creator_password)
        existing_id = decrypted_values.get('evidence_id')
        
        if existing_id is not None:
            existing_ids.add(existing_id)
    
    # Check for duplicates in new IDs
    for new_id in evidence_ids:
        if int(new_id) in existing_ids:  # Convert new_id to int for comparison
            print(f"Error: Evidence ID {new_id} already exists in the blockchain", 
                  file=sys.stderr)
            sys.exit(1)

def run():
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Parse command line arguments
    args = parse_add_args(sys.argv[2:])
    
    # Validate case ID format
    case_id = validate_case_id(args.case_id)
    
    # Create or load blockchain
    blockchain = Blockchain(blockchain_file)
    
    # Initialize blockchain if it doesn't exist
    if not os.path.exists(blockchain_file) or len(blockchain.blocks) == 0:
        blockchain.init_blockchain()
    
    # Convert evidence IDs to integers and validate
    evidence_ids = []
    for item_id in args.item_ids:
        try:
            item_id_int = int(item_id)
            if item_id_int < 0 or item_id_int > 0xFFFFFFFF:
                print(f"Error: Item ID {item_id} must be a 32-bit unsigned integer")
                exit(1)
            evidence_ids.append(item_id_int)
        except ValueError:
            print(f"Error: Item ID {item_id} must be a valid integer")
            exit(1)
    
    # Validate evidence IDs (check for duplicates)
    validate_evidence_ids(blockchain, evidence_ids)
    
    # Validate creator password
    if not validate_password(args.password):
        print("Error: Invalid password", file=sys.stderr)
        sys.exit(1)
    
    # Make sure we're using the creator password
    if args.password != get_role_passwords()['creator']:
        print("Error: Must use creator password for adding items", file=sys.stderr)
        sys.exit(1)
    
    # Add each evidence item
    for item_id in evidence_ids:
        block = Block(
            case_id=case_id,
            evidence_id=item_id,
            state=b"CHECKEDIN",
            creator=args.creator.encode(),
            data=b""
        )
        
        print("\nBlock Values:")
        print(f"case_id=b'{block.case_id}'")
        print(f"evidence_id=b'{block.evidence_id}'")
        
        # Add debug print for decrypted values
        decrypted = block.get_decrypted_values(args.password)
        print(f"\nDecrypted Values:")
        print(f"case_id: {decrypted['case_id']}")
        print(f"evidence_id: {decrypted['evidence_id']}")
        
        blockchain.add_block(block)
        
        chain_block = blockchain.blocks[-1]
        print(f"\nActual chain value for case_id: {chain_block.case_id}")
        
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        print(f"\nAdded item: {item_id}")
        print(f"Status: CHECKEDIN")
        print(f"Time of action: {timestamp}")

if __name__ == "__main__":
    run()
