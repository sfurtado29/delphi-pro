import base64
from Crypto.Cipher import AES

SECRET_KEY = "your32bytekeygoeshere"

def encrypt_value(plaintext: str) -> str:
    if plaintext is None:
        return None
    cipher = AES.new(SECRET_KEY.encode("utf-8"), AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

def decrypt_value(encrypted: str) -> str:
    if encrypted is None:
        return None
    raw = base64.b64decode(encrypted)
    nonce, ciphertext = raw[:16], raw[16:]
    cipher = AES.new(SECRET_KEY.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode("utf-8")