import struct
import time
import hashlib
import uuid
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

class Block:
    FORMAT = '32s d 32s 32s 12s 12s 12s I'
    
    def __init__(self, prev_hash=None, case_id=None, evidence_id=None, 
                 state=None, creator=None, owner=None, data=None, encryption_key=None):
        # Ensure encryption key is exactly 16 bytes
        self.encryption_key = self._pad_to_16_bytes(encryption_key or b'ThisIsASecretKey')
        self.prev_hash = prev_hash if prev_hash else bytes(32)
        self.timestamp = time.time()
        
        # Handle Case ID (UUID)
        if case_id:
            self.case_id_original = case_id
            case_id_bytes = str(case_id).encode()
            self.case_id = self._pad_to_32_bytes(self._encrypt_data(self._pad_to_16_bytes(case_id_bytes)))
        else:
            self.case_id_original = uuid.UUID(int=0)
            self.case_id = bytes(32)
            
        # Handle Evidence ID
        if evidence_id:
            self.evidence_id_original = evidence_id
            evidence_id_bytes = str(evidence_id).encode()
            self.evidence_id = self._pad_to_32_bytes(self._encrypt_data(self._pad_to_16_bytes(evidence_id_bytes)))
        else:
            self.evidence_id_original = 0
            self.evidence_id = bytes(32)
            
        # Handle fixed-length fields
        self.state = self._pad_to_12_bytes(state if state else b"INITIAL")
        self.creator = self._pad_to_12_bytes(creator if creator else b"")
        self.owner = self._pad_to_12_bytes(owner if owner else b"")
        self.data = data if data else b"Initial block\0"
        self.data_length = len(self.data)

    def _pad_to_32_bytes(self, data):
        """Ensure data is exactly 32 bytes"""
        if len(data) > 32:
            return data[:32]
        return data + bytes(32 - len(data))

    def _pad_to_16_bytes(self, data):
        """Ensure data is exactly 16 bytes"""
        if not isinstance(data, bytes):
            data = data.encode()
        if len(data) > 16:
            return data[:16]
        return data + bytes(16 - len(data))

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
        block.timestamp = 0  # Set to 0 instead of current time
        block.case_id = b"0" * 32  # 32 bytes of ASCII '0' characters
        block.evidence_id = b"0" * 32  # 32 bytes of ASCII '0' characters
        block.state = b"INITIAL\0\0\0\0\0"  # Exactly as specified
        block.creator = b"\0" * 12  # 12 null bytes
        block.owner = b"\0" * 12  # 12 null bytes
        block.data = b"Initial block\0"  # Including null terminator
        block.data_length = 14  # Exactly 14 bytes
        return block

    def get_decrypted_values(self, password=None):
        if password == "1234":
            try:
                decrypted_case_id = self._decrypt_data(self.case_id[:16]).rstrip(b'\0')
                decrypted_evidence_id = self._decrypt_data(self.evidence_id[:16]).rstrip(b'\0')
                return {
                    'case_id': decrypted_case_id.decode(),
                    'evidence_id': int(decrypted_evidence_id) if decrypted_evidence_id else 0
                }
            except:
                return {
                    'case_id': self.case_id.hex(),
                    'evidence_id': self.evidence_id.hex()
                }
        return {
            'case_id': self.case_id.hex(),
            'evidence_id': self.evidence_id.hex()
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