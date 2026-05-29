
import base64
from Crypto.Cipher import AES
import os
import logging
 
# SECRETKEY = "1234567890123456" # must be 16/24/32 bytes_

SECRET_KEY = os.getenv("AES_SECRET_KEY", "1234567890123456").encode("utf-8")
 
def encrypt_value(plaintext: str) -> str:
    """Encrypt a string using AES EAX and return base64 (nonce + ciphertext + tag)."""
    if plaintext is None:
        return None
    try:
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        encrypted_data = cipher.nonce + ciphertext + tag
        return base64.b64encode(encrypted_data).decode("utf-8")
    except Exception as e:
        logging.error(f"Encryption error for value={plaintext}: {e}")
    return None


def decrypt_value(encrypted: str) -> str:
    """Decrypt a base64 string back to plaintext.
    If not valid encrypted data, return as-is."""
    if not encrypted:
        return None
    try:
        raw = base64.b64decode(encrypted)
 
        nonce, ciphertext, tag = raw[:16], raw[16:-16], raw[-16:]
        
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode("utf-8")
    except Exception as e:
        logging.error(f"Decryption failed for value: {encrypted}, error: {e}")
        return encrypted
    

        # def encryptvalue(plaintext: str) -> str:_
        # """Encrypt a string and return base64 (nonce + tag + ciphertext)."""
        # if plaintext is None:
        # return None
        # cipher = AES.new(SECRETKEY, AES.MODE_EAX)_
        # ciphertext, tag = cipher.encryptand_digest(plaintext.encode("utf-8"))_
        # return base64.b64encode(cipher.nonce + tag + ciphertext).decode("utf-8")
        
        # def decryptvalue(encrypted: str) -> str:_
        # """Decrypt a base64 string back to plaintext.
        # If not valid encrypted data, return as-is."""
        # if encrypted is None:
        # return None
        # try:
        # raw = base64.b64decode(encrypted)
        # nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
        # cipher = AES.new(SECRETKEY, AES.MODE_EAX, nonce=nonce)_
        # plaintext = cipher.decryptand_verify(ciphertext, tag)_
        # return plaintext.decode("utf-8")
        # except Exception:
        # # If value is not valid Base64 or not properly encrypted, return as-is
        # return encrypted