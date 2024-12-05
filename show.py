import os
import sys
import argparse
from blockchain import Blockchain
from utils import validate_password, get_role_passwords, get_owner

def parse_show_args(args):
    """
    Parse arguments for the `show` command.
    """
    parser = argparse.ArgumentParser(description='Show cases or items')
    subparsers = parser.add_subparsers(dest="subcommand", required=True, help="Subcommand to execute")

    # Subcommand: show cases
    cases_parser = subparsers.add_parser("cases", help="Show all cases")

    # Subcommand: show items
    items_parser = subparsers.add_parser("items", help="Show items in a case")
    items_parser.add_argument('-c', '--case_id', required=True, help='Case identifier')

    return parser.parse_args(args)

def show_items(case_id):
    """
    Logic to display items in a specific case.
    """
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')

    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)

    try:
        blockchain = Blockchain(blockchain_file)
        found_items = False
        
        print(f"Items in case {case_id}:")
        for block in blockchain.blocks:
            if block.case_id == case_id:
                found_items = True
                print(f"- Evidence ID: {block.evidence_id}")

        if not found_items:
            print(f"No items found for case ID: {case_id}")
            exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

def run():
    """
    Main entry point for the script.
    """
    import sys
    args = parse_show_args(sys.argv[2:])  # Skip the first two arguments (script name and command)

    # Handle the subcommands
    if args.subcommand == "cases":
        showCases()
    elif args.subcommand == "items":
        show_items(args.case_id)

if __name__ == "__main__":
    run()

def showCases():
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)

    # Load the blockchain
    blockchain = Blockchain(blockchain_file)
    caseList = []

    creator_password = get_role_passwords()['creator']

    for block in blockchain.blocks:
        # ignore genesis block
        if block.state == b"INITIAL\0\0\0\0\0":
            continue
        
        # decrypt the blocks
        decrypted_values = block.get_decrypted_values(creator_password)

        # add case ID's to list if it is unique
        if decrypted_values['case_id'] not in caseList:
            caseList.append(decrypted_values['case_id'])

    for case in caseList:
        print(f"{case}")