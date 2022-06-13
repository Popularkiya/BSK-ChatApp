from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import hashlib
import cryptofunc.AESCrypto as AESCrypto
import cryptofunc.SessionKeyCrypto as SessionKeyCrypto


def generateKeyPair():
    key = RSA.generate(2048)

    private = key.export_key()
    public = key.public_key().export_key()

    # print(private)
    # print(public)

    return private, public


def generateDummyPrivateKey():
    key = RSA.generate(2048)

    return key.export_key()


def generateHash(password):
    return hashlib.blake2s(bytes(password, "utf-8"), digest_size=32).digest()


# encrypts and saves key to file
def saveKey(key, hashedPass, path):
    encrypted = AESCrypto.encrypt(key, hashedPass)

    with open(path+"key", "w+b") as f:
        f.write(encrypted)


# decrypts the key and returns it
def getKey(hashedPass, path):
    with open(path+"key", "r+b") as f:
        data = f.read()
        return AESCrypto.decrypt(data, hashedPass)


def encrypt(data, key, dummyPrivateKey=None):
    try:
        rsaKey = RSA.import_key(key)
    except:
        rsaKey = RSA.import_key(dummyPrivateKey)

    cipher = PKCS1_OAEP.new(rsaKey)
    encrypted = cipher.encrypt(data)

    return encrypted


def decrypt(data, key):
    rsaKey = RSA.import_key(key)
    cipher = PKCS1_OAEP.new(rsaKey)

    try:
        decrypted = cipher.decrypt(data)
    except:
        decrypted = SessionKeyCrypto.generate(32)

    return decrypted
