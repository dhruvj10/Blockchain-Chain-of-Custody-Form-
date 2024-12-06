import os
import sys
import argparse
from datetime import datetime
from blockchain import Blockchain
from utils import validate_password, get_role_passwords, get_owner

# Function generated with the help of ChatGPT, OpenAI
def parse_show_args(args):
    parser = argparse.ArgumentParser(description='Show cases or items')
    subparsers = parser.add_subparsers(dest="subcommand", required=True, help="Subcommand to execute")

    # Subcommand: show cases
    cases_parser = subparsers.add_parser("cases", help="Show all cases")

    # Subcommand: show items
    items_parser = subparsers.add_parser("items", help="Show items in a case")
    items_parser.add_argument('-c', '--case_id', required=True, help='Case identifier')

    history_parser = subparsers.add_parser("history", help="Show case history")
    history_parser.add_argument('-c', '--case_id', required=False, help='Case identifier')
    history_parser.add_argument('-i', '--item_id', required=False, help='Item identifier')
    history_parser.add_argument('-r', '--reverse', action='store_true', help="Reverse history")
    history_parser.add_argument('-p', '--password', required=False, help='password')
    history_parser.add_argument('-n', '--num_entries', required=False, type=int, help="Number of entries in output")

    return parser.parse_args(args)

def showItems(case_id):
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)

    # Load the blockchain
    blockchain = Blockchain(blockchain_file)
    itemsList = []

    creator_password = get_role_passwords()['creator']

    for block in blockchain.blocks:
        # ignore genesis block
        if block.state == b"INITIAL\0\0\0\0\0":
            continue
        
        # decrypt the blocks
        decrypted_values = block.get_decrypted_values(creator_password)

        # add case ID's to list if it is unique
        if decrypted_values['case_id'] == case_id and decrypted_values['evidence_id'] not in itemsList:
            itemsList.append(decrypted_values['evidence_id'])

    for item in itemsList:
        print(f"{item}")

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

def showHistory(case_id = None, item_id = None, reverse = None, password=None, num_entries=None):
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)
    
    if password and not validate_password(password=password):
        print("Error: Invalid password")
        sys.exit(1)

    # Load the blockchain
    blockchain = Blockchain(blockchain_file)
    historyBlocks = []

    creator_password = get_role_passwords()['creator']

    for block in blockchain.blocks:
        # default: do not add block to list
        found = False
        
        # decrypt the blocks
        decrypted_values = block.get_decrypted_values(creator_password)

        # check if case id matches
        if case_id and decrypted_values['case_id'] == case_id:
            found = True

        # check if evidence_id matches
        if item_id and int(decrypted_values['evidence_id']) == int(item_id):
            found = True
  
        # if both are none, print all 
        if not case_id and not item_id:
            found = True

        if found and block not in historyBlocks:
            data = {
                "Case": "",
                "Item": decrypted_values['evidence_id'],
                "Action": block.state.rstrip(b'\x00').decode(),
                "Time": datetime.fromtimestamp(block.timestamp).isoformat() + "Z"
            }

            if password:
                data['Case'] = decrypted_values['case_id']
            else:
                data['Case'] = block.case_id

            if block.state.rstrip(b'\x00').decode() == 'INITIAL':
                data['Case'] = '00000000-0000-0000-0000-000000000000'
                data['Item'] = 0

            if not reverse:
                historyBlocks.append(data)
            else:
                historyBlocks = [data] + historyBlocks

    if num_entries and num_entries < len(historyBlocks):
        historyBlocks = historyBlocks[:num_entries]

    for block in historyBlocks:
        for key in block:
            print(f"{key}: {block[key]}")
        print()



def run():
    args = parse_show_args(sys.argv[2:])

    if args.subcommand == "cases":
        showCases()
    elif args.subcommand == "items":
        showItems(args.case_id)
    elif args.subcommand == "history":
        showHistory(args.case_id, args.item_id, args.reverse, args.password, args.num_entries)

