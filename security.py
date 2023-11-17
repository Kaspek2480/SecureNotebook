import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# unsafe but still better than using four digit pin instead deriving key from user input
salt = b"saltysalt"


def calculate_key(user_input):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=48,
        salt=salt,
        iterations=1_000_000,
    )
    result = kdf.derive(user_input.encode())

    # first 32 bytes are the key, last 16 bytes are the iv
    return {'key': result[:32], 'iv': result[32:]}


def encrypt_text(aes_key, aes_iv, plaintext):
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())

    # Użyj PKCS7 padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext.hex()


def decrypt_text(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Usuń PKCS7 padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()

    return plaintext.decode(encoding='utf-8')


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def create_pin_hash(pin):
    key_pair = calculate_key(pin)
    key = key_pair['key']
    iv = key_pair['iv']
    pin_hash = sha256((key + iv).hex())
    return pin_hash


if __name__ == "__main__":
    key_pair = calculate_key("test")
    key = key_pair['key']
    iv = key_pair['iv']

    plaintext = b'your_text_here'

    enc_text = encrypt_text(key, iv, plaintext)
    print("Encrypted text:", enc_text.hex())
    dec_text = decrypt_text(key, iv, enc_text)
    print("Decrypted text:", dec_text)
