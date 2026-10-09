from cryptography.fernet import Fernet
import base64
import hashlib


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_file(file_data, password):
    key = generate_key(password)
    fernet = Fernet(key)
    return fernet.encrypt(file_data)


def decrypt_file(file_data, password):
    key = generate_key(password)
    fernet = Fernet(key)
    return fernet.decrypt(file_data)
