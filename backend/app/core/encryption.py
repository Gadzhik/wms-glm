"""Encryption utilities for video archive using AES-256-GCM"""
import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


class VideoEncryption:
    """Video encryption using AES-256-GCM"""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption
        
        Args:
            key: 32-byte encryption key. If None, generates a new key.
        """
        if key is None:
            self.key = self.generate_key()
        else:
            if len(key) != 32:
                raise ValueError("Key must be 32 bytes (256 bits)")
            self.key = key
        self.aesgcm = AESGCM(self.key)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new 32-byte encryption key
        
        Returns:
            32-byte encryption key
        """
        return os.urandom(32)
    
    @staticmethod
    def generate_nonce() -> bytes:
        """Generate a new 12-byte nonce
        
        Returns:
            12-byte nonce
        """
        return os.urandom(12)
    
    def encrypt(self, data: bytes, nonce: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """Encrypt data using AES-256-GCM
        
        Args:
            data: Data to encrypt
            nonce: Optional nonce. If None, generates a new one.
            
        Returns:
            Tuple of (encrypted_data, nonce)
        """
        if nonce is None:
            nonce = self.generate_nonce()
        
        encrypted_data = self.aesgcm.encrypt(nonce, data, None)
        return encrypted_data, nonce
    
    def decrypt(self, encrypted_data: bytes, nonce: bytes) -> bytes:
        """Decrypt data using AES-256-GCM
        
        Args:
            encrypted_data: Encrypted data
            nonce: Nonce used for encryption
            
        Returns:
            Decrypted data
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            decrypted_data = self.aesgcm.decrypt(nonce, encrypted_data, None)
            return decrypted_data
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def encrypt_file(self, input_path: str, output_path: str) -> bytes:
        """Encrypt a file
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
            
        Returns:
            Nonce used for encryption
        """
        with open(input_path, "rb") as f:
            data = f.read()
        
        encrypted_data, nonce = self.encrypt(data)
        
        with open(output_path, "wb") as f:
            f.write(encrypted_data)
        
        return nonce
    
    def decrypt_file(self, input_path: str, output_path: str, nonce: bytes) -> None:
        """Decrypt a file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
            nonce: Nonce used for encryption
        """
        with open(input_path, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt(encrypted_data, nonce)
        
        with open(output_path, "wb") as f:
            f.write(decrypted_data)
    
    def encrypt_chunk(self, chunk: bytes, nonce: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """Encrypt a data chunk (for streaming)
        
        Args:
            chunk: Data chunk to encrypt
            nonce: Optional nonce. If None, generates a new one.
            
        Returns:
            Tuple of (encrypted_chunk, nonce)
        """
        return self.encrypt(chunk, nonce)
    
    def decrypt_chunk(self, encrypted_chunk: bytes, nonce: bytes) -> bytes:
        """Decrypt a data chunk (for streaming)
        
        Args:
            encrypted_chunk: Encrypted data chunk
            nonce: Nonce used for encryption
            
        Returns:
            Decrypted chunk
        """
        return self.decrypt(encrypted_chunk, nonce)
    
    def get_key_base64(self) -> str:
        """Get encryption key as base64 string
        
        Returns:
            Base64 encoded key
        """
        return base64.b64encode(self.key).decode('utf-8')
    
    @classmethod
    def from_base64_key(cls, key_b64: str) -> "VideoEncryption":
        """Create VideoEncryption from base64 encoded key
        
        Args:
            key_b64: Base64 encoded key
            
        Returns:
            VideoEncryption instance
        """
        key = base64.b64decode(key_b64.encode('utf-8'))
        return cls(key)


def encrypt_data(data: bytes, key: bytes, nonce: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """Encrypt data using AES-256-GCM
    
    Args:
        data: Data to encrypt
        key: 32-byte encryption key
        nonce: Optional nonce. If None, generates a new one.
        
    Returns:
        Tuple of (encrypted_data, nonce)
    """
    encryption = VideoEncryption(key)
    return encryption.encrypt(data, nonce)


def decrypt_data(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypt data using AES-256-GCM
    
    Args:
        encrypted_data: Encrypted data
        key: 32-byte encryption key
        nonce: Nonce used for encryption
        
    Returns:
        Decrypted data
    """
    encryption = VideoEncryption(key)
    return encryption.decrypt(encrypted_data, nonce)


def generate_encryption_key() -> bytes:
    """Generate a new 32-byte encryption key
    
    Returns:
        32-byte encryption key
    """
    return VideoEncryption.generate_key()


def generate_encryption_key_base64() -> str:
    """Generate a new encryption key and return as base64 string
    
    Returns:
        Base64 encoded encryption key
    """
    key = generate_encryption_key()
    return base64.b64encode(key).decode('utf-8')
