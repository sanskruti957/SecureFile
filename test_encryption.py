
from encryption import encrypt_file, decrypt_file
from cryptography.fernet import InvalidToken


def test_encrypt_and_decrypt():
    original_data = b"Hello SecureFile!"
    password = "test123"

    encrypted_data = encrypt_file(original_data, password)
    decrypted_data = decrypt_file(encrypted_data, password)

    assert encrypted_data != original_data
    assert decrypted_data == original_data


def test_wrong_password():
    original_data = b"Secret information"
    encrypted_data = encrypt_file(original_data, "correct123")

    try:
        decrypt_file(encrypted_data, "wrong123")
        assert False, "Wrong password should fail"
    except InvalidToken:
        pass