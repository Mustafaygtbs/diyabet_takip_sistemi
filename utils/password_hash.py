# utils/password_hash.py
import hashlib
import os
import binascii

class PasswordHasher:
    @staticmethod
    def hash_password(password):
        """
        Şifreyi güvenli bir şekilde hash'ler.
        
        :param password: Hash'lenecek şifre
        :return: Hash'lenmiş şifre
        """
        # Salt oluşturma
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        # PBKDF2 ile hash'leme
        hash_bytes = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        hash_hex = binascii.hexlify(hash_bytes)
        # Salt ve hash'i birleştirme
        return (salt + hash_hex).decode('ascii')
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """
        Girilen şifreyi hash'lenmiş şifre ile karşılaştırır.
        
        :param stored_password: Veritabanında depolanan hash'lenmiş şifre
        :param provided_password: Kullanıcının girdiği şifre
        :return: Şifreler eşleşiyorsa True, aksi halde False
        """
        salt = stored_password[:64]
        stored_hash = stored_password[64:]
        
        # Aynı salt ile hash'leme
        hash_bytes = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), 
                                          salt.encode('ascii'), 100000)
        hash_hex = binascii.hexlify(hash_bytes).decode('ascii')
        
        return hash_hex == stored_hash