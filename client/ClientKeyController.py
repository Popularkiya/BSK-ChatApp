from os import path, makedirs
import cryptofunc.RSACrypto as RSACrypto
import cryptofunc.AESCrypto as AESCrypto
import cryptofunc.SessionKeyCrypto as SessionKeyCrypto

KEYS_PATH = "keys\\"
PRIVATE_KEY_PATH = "\\private\\"
PUBLIC_KEY_PATH = "\\public\\"


class ClientKeyController:
    def __init__(self, name, password):
        self.name = name
        self.password = password

        self.keyPath = KEYS_PATH + name
        self.privateKeyPath = self.keyPath + PRIVATE_KEY_PATH
        self.publicKeyPath = self.keyPath + PUBLIC_KEY_PATH

        self.lastSessionKey = None
        self.dummyPrivateKey = None

    def getKeys(self):
        hashedPass = RSACrypto.generateHash(self.password)

        if not path.exists(self.keyPath):
            makedirs(self.privateKeyPath)
            makedirs(self.publicKeyPath)

            private, public = RSACrypto.generateKeyPair()
            self.dummyPrivateKey = RSACrypto.generateDummyPrivateKey()

            RSACrypto.saveKey(private, hashedPass, self.privateKeyPath)
            RSACrypto.saveKey(public, hashedPass, self.publicKeyPath)

            return private, public
        else:
            try:
                private = RSACrypto.getKey(hashedPass, self.privateKeyPath)
                public = RSACrypto.getKey(hashedPass, self.publicKeyPath)
            except:
                private, public = RSACrypto.generateKeyPair()
                self.dummyPrivateKey = RSACrypto.generateDummyPrivateKey()

            return private, public

    def generateSessionKey(self, length):
        return SessionKeyCrypto.generate(length)

    def encryptSessionKey(self, sessionKey, encryptionKey):
        return RSACrypto.encrypt(sessionKey, encryptionKey, self.dummyPrivateKey)

    def decryptSessionKey(self, sessionKey, decryptionKey):
        return RSACrypto.decrypt(sessionKey, decryptionKey)

    def encryptData(self, data, secretKey, mode):
        encryptedData = AESCrypto.encrypt(data, secretKey, mode)

        return encryptedData

    def decryptData(self, data, secretKey, mode):
        decryptedData = AESCrypto.decrypt(data, secretKey, mode)

        return decryptedData
