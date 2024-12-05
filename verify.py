import os
from blockchain import Blockchain
from utils import get_role_passwords

def verify_blockchain():
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)
    
    try:
        blockchain = Blockchain(blockchain_file)
        
        if len(blockchain.blocks) == 0:
            print("Error: blockchain is empty")
            exit(1)
        
        # Track state of each evidence item
        evidence_states = {}  # Dictionary to track the latest state of each item
        creator_password = get_role_passwords()['creator']
        
        # Define terminal states
        terminal_states = [b"DESTROYED", b"DISPOSED", b"RELEASED"]
        
        # Verify the initial block (genesis block)
        genesis_block = blockchain.blocks[0]
        if not (genesis_block.prev_hash == bytes(32) and
                genesis_block.state.rstrip(b'\0') == b"INITIAL" and
                len(genesis_block.state) == 12 and
                len(genesis_block.creator) == 12 and
                len(genesis_block.owner) == 12):
            print("Error: invalid genesis block")
            exit(1)
        
        # Verify chain of hashes and block integrity
        for i in range(1, len(blockchain.blocks)):
            current_block = blockchain.blocks[i]
            previous_block = blockchain.blocks[i-1]
            
            # Verify previous hash matches
            if current_block.prev_hash != previous_block.calculate_hash():
                print(f"Error: invalid hash chain at block {i}")
                exit(1)
            
            # Verify block state is valid
            valid_states = [b"CHECKEDIN\x00\x00", b"CHECKEDOUT\x00", b"DISPOSED\x00\x00\x00", b"DESTROYED\x00\x00", b"RELEASED\x00\x00\x00"]
            if current_block.state.rstrip(b'\0') not in [state.rstrip(b'\0') for state in valid_states]:
                print(f"Error: invalid state at block {i}")
                exit(1)
            
            # Get evidence ID
            decrypted_values = current_block.get_decrypted_values(creator_password)
            evidence_id = decrypted_values['evidence_id']
            current_state = current_block.state.rstrip(b'\0')
            
            # Check for invalid state transitions
            if evidence_id in evidence_states:
                last_state = evidence_states[evidence_id]
                
                # Check if item is being removed after already being in a terminal state
                if last_state in terminal_states and current_state in terminal_states:
                    print(f"Error: evidence item {evidence_id} was removed twice")
                    exit(1)
                
                # If item was removed, it cannot transition to any other state
                if last_state in terminal_states and current_state in [b"CHECKEDIN", b"CHECKEDOUT"]:
                    print(f"Error: evidence item {evidence_id} was checked in or out after being removed")
                    exit(1)
                
                # If item is already checked in, it cannot be checked in again without being checked out
                if last_state == b"CHECKEDIN" and current_state == b"CHECKEDIN":
                    print(f"Error: evidence item {evidence_id} was checked in twice without a checkout")
                    exit(1)
                
                # If item is already checked out, it cannot be checked out again without being checked in
                if last_state == b"CHECKEDOUT" and current_state == b"CHECKEDOUT":
                    print(f"Error: evidence item {evidence_id} was checked out twice without a checkin")
                    exit(1)
            
            # Update evidence state
            evidence_states[evidence_id] = current_state
            
            # Verify fixed-length fields
            if (len(current_block.creator) != 12 or
                len(current_block.owner) != 12 or
                len(current_block.state) != 12):
                print(f"Error: invalid field length at block {i}")
                exit(1)
            
            # Verify data length matches actual data
            if len(current_block.data) != current_block.data_length:
                print(f"Error: invalid data length at block {i}")
                exit(1)
        
        print("Blockchain verification passed")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

def run():
    verify_blockchain()

if __name__ == "__main__":
    run()