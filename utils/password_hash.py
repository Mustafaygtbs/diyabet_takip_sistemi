# utils/password_hash.py
import hashlib
import os
import binascii

class PasswordHasher:
    @staticmethod
    def hash_password(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        hash_bytes = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        hash_hex = binascii.hexlify(hash_bytes)
        return (salt + hash_hex).decode('ascii')
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        salt = stored_password[:64]
        stored_hash = stored_password[64:]
        
        hash_bytes = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), 
                                          salt.encode('ascii'), 100000)
        hash_hex = binascii.hexlify(hash_bytes).decode('ascii')
        
        return hash_hex == stored_hash