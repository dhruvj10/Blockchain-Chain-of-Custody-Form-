#!/usr/bin/env python3
#Driver File - runs the program 
import os
import importlib
import logging
import sys

# Get blockchain file path from environment variable
BLOCKCHAIN_FILE = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')

def load_modules():
    modules = {}
    for filename in os.listdir('.'):
        if filename.endswith('.py') and filename != 'main.py':
            module_name = filename[:-3]
            module = importlib.import_module(module_name)
            modules[module_name] = module
    return modules

def main():
    
    # Get command from command line arguments
    if len(sys.argv) < 2:
        print("Error: No command provided")
        sys.exit(1)

    command = sys.argv[1].lower()
    
    if command == 'init':
        # Check for additional parameters
        if len(sys.argv) > 2:
            print("Error: init command takes no parameters")
            sys.exit(1)
            
        if os.path.exists(BLOCKCHAIN_FILE):
            try:
                from block import Block
                from blockchain import Blockchain
                
                # Try to load the blockchain - this will validate the file structure
                blockchain = Blockchain(BLOCKCHAIN_FILE)
                if len(blockchain.blocks) > 0:  # If we can load blocks, file is valid
                    print("Blockchain already initialized")
                    sys.exit(0)
                else:  # No valid blocks found
                    print(f"Error: Failed to load blockchain from {BLOCKCHAIN_FILE}")
                    sys.exit(1)
            except Exception as e:
                print(f"Error: Failed to load blockchain from {BLOCKCHAIN_FILE}")
                sys.exit(1)
        else:
            # Create new blockchain file with initial block
            try:
                from block import Block
                from blockchain import Blockchain
                
                # Create blockchain with the specified file
                blockchain = Blockchain(BLOCKCHAIN_FILE)
                # Initialize it with genesis block
                blockchain.init_blockchain()
                
                print("Blockchain initialized")
                sys.exit(0)
            except Exception as e:
                print(f"Error: Failed to create blockchain file: {str(e)}")
                sys.exit(1)
    elif command == 'add':
        try:
            from add import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == 'verify':
        try:
            from verify import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == 'dump':
        try:
            from show_history import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == 'show':
        try:
            from show import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == 'checkout':
        try:
            from checkout import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == 'checkin':
        try:
            from checkin import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    elif command == "remove":
        try:
            from remove import run
            run()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        print(f"{command == 'remove'}")
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()