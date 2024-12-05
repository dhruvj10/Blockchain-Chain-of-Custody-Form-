import os
import sys
from blockchain import Blockchain
from utils import validate_password, get_role_passwords, get_owner

def run():
    if sys.argv[2] == 'cases':
        showCases()
    elif sys.argv[2] == 'items':
        showItems()

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
        print(f"Case:\t{case}")

def showItems():
    pass


# def run():
#     blockchain = Blockchain()
#     password = input("Enter password (or press Enter to view encrypted values): ").strip()
    
#     for i, block in enumerate(blockchain.blocks):
#         print(f"\nBlock {i}:")
#         values = block.get_decrypted_values(password)
        
#         # Display timestamp in human-readable format
#         timestamp = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
#         print(f"Timestamp: {timestamp}")
#         print(f"Previous Hash: {binascii.hexlify(block.prev_hash).decode()}")
#         print(f"Case ID: {values['case_id']}")
#         print(f"Evidence ID: {values['evidence_id']}")
        
#         # Decode and display text fields, stripping null bytes
#         try:
#             state = block.state.decode('utf-8').rstrip('\0')
#         except UnicodeDecodeError:
#             state = binascii.hexlify(block.state).decode()
#         print(f"State: {state}")
        
#         try:
#             creator = block.creator.decode('utf-8').rstrip('\0')
#         except UnicodeDecodeError:
#             creator = binascii.hexlify(block.creator).decode()
#         print(f"Creator: {creator}")
        
#         try:
#             owner = block.owner.decode('utf-8').rstrip('\0')
#         except UnicodeDecodeError:
#             owner = binascii.hexlify(block.owner).decode()
#         print(f"Owner: {owner}")
        
#         try:
#             data = block.data.decode('utf-8').rstrip('\0')
#         except UnicodeDecodeError:
#             data = binascii.hexlify(block.data).decode()
#         print(f"Data: {data}")