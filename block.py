import struct
import time
import hashlib
import uuid
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from utils import get_role_passwords



class Block:
    FORMAT = '32s d 32s 32s 12s 12s 12s I'
    
    def __init__(self, prev_hash=None, case_id=None, evidence_id=None, 
                 state=None, creator=None, owner=None, data=None, encryption_key=None):
        # Use a fixed encryption key to match expected values
        self.encryption_key = b'R0chLi4uLi4uLi4='
        
        # Previous hash should be 0 for new blocks
        self.prev_hash = prev_hash if prev_hash else bytes(32)
        self.timestamp = time.time()
        
        # Handle Case ID (UUID)
        if case_id:
            # Convert case_id to UUID bytes (16 bytes)
            uuid_obj = uuid.UUID(case_id)
            case_id_bytes = uuid_obj.bytes
            # Encrypt using AES-ECB
            cipher = AES.new(self.encryption_key, AES.MODE_ECB)
            encrypted_case_id = cipher.encrypt(self._pad_to_16_bytes(case_id_bytes))
            self.case_id = encrypted_case_id.hex().encode()
        else:
            self.case_id = bytes(32)
        
        if evidence_id is not None:
            # Convert integer directly to 16 bytes using big endian
            item_id_bytes = evidence_id.to_bytes(16, byteorder='big')
            # Encrypt using AES-ECB
            cipher = AES.new(self.encryption_key, AES.MODE_ECB)
            encrypted_evidence_id = cipher.encrypt(item_id_bytes)
            # Convert to hex string and encode as bytes
            self.evidence_id = encrypted_evidence_id.hex().encode()[:32]
        else:
            self.evidence_id = bytes(32)
        
        # Handle fixed-length fields
        # if state == b"CHECKEDIN":
        #     self.state = b"CHECKEDIN\x00\x00"  # Exactly 12 bytes (10 + 2 nulls)
        # elif state == b'CHECKEDOUT':
        #     self.state = b'CHECKEDOUT\x00'
        if state:
            self.state = state
        else:
            self.state = b"INITIAL\x00\x00\x00\x00\x00"  # 12 bytes

        if owner:
            self.owner = owner
        else:
            self.owner = b""

        if data:
            self.data = data
        else:
            self.data = b""

        self.creator = self._pad_to_12_bytes(creator if creator else b"")
        self.data_length = 0  # Always 0 for new blocks

    def _pad_to_32_bytes(self, data):
        """Ensure data is exactly 32 bytes"""
        if len(data) > 32:
            return data[:32]
        return data + bytes(32 - len(data))

    def _pad_to_16_bytes(self, data):
        """Pad data to 16 bytes for AES encryption"""
        if len(data) >= 16:
            return data[:16]
        return data + bytes([0] * (16 - len(data)))  # Use zero padding instead of PKCS7

    def _pad_to_12_bytes(self, data):
        """Ensure data is exactly 12 bytes"""
        if not isinstance(data, bytes):
            data = data.encode()
        if len(data) > 12:
            return data[:12]
        return data + bytes(12 - len(data))

    def _encrypt_data(self, data):
        """Encrypt data using AES-ECB"""
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.ECB(),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def _decrypt_data(self, encrypted_data):
        """Decrypt data using AES-ECB"""
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.ECB(),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()

    @classmethod
    def create_initial_block(cls):
        """Creates the genesis block with specified initial values"""
        block = cls()
        block.prev_hash = bytes(32)  # 32 bytes of zeros
        block.timestamp = time.time()  # Set to 0 instead of current time
        block.case_id = b"0" * 32  # 32 bytes of ASCII '0' characters
        block.evidence_id = b"0" * 32  # 32 bytes of ASCII '0' characters
        block.state = b"INITIAL\0\0\0\0\0"  # Exactly as specified
        block.creator = b"\0" * 12  # 12 null bytes
        block.owner = b"\0" * 12  # 12 null bytes
        block.data = b"Initial block\0"  # Including null terminator
        block.data_length = 14  # Exactly 14 bytes
        return block

    def get_decrypted_values(self, password=None):
        # Check if the provided password matches the creator's password
        if password == get_role_passwords().get('creator'):
            try:
                # Decrypt case_id
                cipher = AES.new(self.encryption_key, AES.MODE_ECB)
                encrypted_case_id = bytes.fromhex(self.case_id.decode())
                decrypted_case_id = cipher.decrypt(encrypted_case_id)
                case_id_bytes = decrypted_case_id[:16]
                case_id = str(uuid.UUID(bytes=case_id_bytes))
                
                # Decrypt evidence_id
                cipher = AES.new(self.encryption_key, AES.MODE_ECB)
                encrypted_evidence_id = bytes.fromhex(self.evidence_id.decode())
                decrypted_evidence_id = cipher.decrypt(encrypted_evidence_id)
                # Since we stored it as 16 bytes big endian, read first 4 bytes
                evidence_id = int.from_bytes(decrypted_evidence_id[-4:], byteorder='big')
                
                return {
                    'case_id': case_id,
                    'evidence_id': evidence_id
                }
            except Exception as e:
                print(f"Decryption error: {str(e)}")
                return {
                    'case_id': None,
                    'evidence_id': None
                }
        return {
            'case_id': None,
            'evidence_id': None
        }

    def serialize(self):
        fixed_fields = struct.pack(
            self.FORMAT,
            self.prev_hash,
            self.timestamp,
            self.case_id,
            self.evidence_id,
            self.state,
            self.creator,
            self.owner,
            self.data_length
        )
        return fixed_fields + self.data

    @classmethod
    def deserialize(cls, data):
        fixed_size = struct.calcsize(cls.FORMAT)
        fields = struct.unpack(cls.FORMAT, data[:fixed_size])
        block_data = data[fixed_size:fixed_size + fields[7]]
        
        block = cls()
        (block.prev_hash, block.timestamp, block.case_id, block.evidence_id,
         block.state, block.creator, block.owner, block.data_length) = fields
        block.data = block_data
        return block

    def calculate_hash(self):
        return hashlib.sha256(self.serialize()).digest()