import argparse
import uuid
import datetime
from block import Block
from blockchain import Blockchain
import os
import sys

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
    # Check if any evidence IDs already exist in the blockchain
    for block in blockchain.blocks:
        decrypted_values = block.get_decrypted_values("1234")
        for evidence_id in evidence_ids:
            try:
                existing_id = decrypted_values['evidence_id']
                # Convert both to strings for comparison
                if str(existing_id) == str(evidence_id):
                    print(f"Error: Evidence ID {evidence_id} already exists in the blockchain")
                    exit(1)
            except (ValueError, TypeError):
                continue

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
            # Ensure it's a valid integer
            evidence_id = int(item_id)
            if evidence_id < 0 or evidence_id > 0xFFFFFFFF:  # Check if it fits in 4 bytes
                print(f"Error: Evidence ID {item_id} must be a 32-bit unsigned integer")
                exit(1)
            evidence_ids.append(str(evidence_id))
        except ValueError:
            print(f"Error: Evidence ID {item_id} must be a valid integer")
            exit(1)
    
    # Validate evidence IDs (check for duplicates)
    validate_evidence_ids(blockchain, evidence_ids)
    
    # Add each evidence item
    for item_id in evidence_ids:
        # Create new block
        block = Block(
            case_id=case_id,
            evidence_id=item_id,
            state=b"CHECKEDIN",
            creator=args.creator.encode(),
            data=b""  # Empty data field
        )
        
        # Print block values before adding to blockchain
        print("\nBlock Values:")
        print(f"case_id=b'{block.case_id}'")
        print(f"evidence_id=b'{block.evidence_id}'")
        
        # Add block to blockchain
        blockchain.add_block(block)
        
        # Print the exact value from the chain
        chain_block = blockchain.blocks[-1]  # Get the last added block
        print(f"\nActual chain value for case_id: {chain_block.case_id}")
        
        # Get current time in ISO format with Z suffix
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Print output
        print(f"\nAdded item: {item_id}")
        print(f"Status: CHECKEDIN")
        print(f"Time of action: {timestamp}")

if __name__ == "__main__":
    run()