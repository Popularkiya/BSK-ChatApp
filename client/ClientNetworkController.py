import socket
import threading
from styles.styles import *
from tkinter import ttk
import tqdm
import os
from frame.Frame import *
import struct
from client.ClientKeyController import ClientKeyController

SERVER = "192.168.1.100" # "192.168.178.25"
PORT = 9090


class ClientNetworkController:
    def __init__(self, clientName, keyController: ClientKeyController):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")

        self.clientName = clientName
        self.keyController = keyController
        self.serverAddr = SERVER
        self.serverPort = PORT
        self.view = None
        self.running = True
        self.recipientPublicKey = None
        self.recipientName = ""
        self.cipherMode = "ECB"

        self.s.connect((self.serverAddr, self.serverPort))
        print(f"Connected to server {self.serverAddr}:{self.serverPort}")

    def startCommunication(self):
        # function to basically start the thread for receiving messages
        self.receivingThread = threading.Thread(target=self.receiveMessages, args=())
        self.receivingThread.start()

        self.publishPublicKey()
        self.requestPublicKey()

    def requestPublicKey(self):
        self.sendFrame(Frame(FrameType.HELLO_REQ, "", user=self.clientName))

    def publishPublicKey(self):
        _, publicKey = self.keyController.getKeys()
        self.sendFrame(Frame(FrameType.HELLO, publicKey, user=self.clientName))

    def stopCommunication(self):
        # send close connection command to server (for that client)
        self.sendFrame(Frame(FrameType.CLOSE, "", user=self.clientName))
        self.running = False

        # close connection
        self.s.shutdown(socket.SHUT_WR)
        self.s.close()
        print("Disconnecting...")
        self.view.rootWindow.destroy()

    def receiveMessages(self):
        if self.view is None:
            print("Chat view isn't assigned!")
            return

        default_size = len(Frame(FrameType.SIZE, struct.pack('I', 420)).serialize())
        size = default_size

        while self.running:
            try:
                message = self.s.recv(size)
                recvFrame = pickle.loads(message)
                size = default_size

                frameType = recvFrame.type
                if frameType == FrameType.MSG or frameType == FrameType.FILE or frameType == FrameType.FILE_END:
                    self.cipherMode = recvFrame.mode
                    sessionKey = self.keyController.lastSessionKey
                    try:
                        recvFrame.data = self.keyController.decryptData(recvFrame.data, sessionKey, self.cipherMode)
                    except:
                        pass

                if recvFrame.type == FrameType.SIZE:
                    size = struct.unpack('I', recvFrame.data)
                    size = size[0]

                elif recvFrame.type == FrameType.ACK:
                    self.view.displayAcknowledgement(recvFrame.user)

                elif recvFrame.type == FrameType.FILE_END:
                    self.view.displayMessage(f"{recvFrame.user} sent {recvFrame.fileName}")
                    self.sendAcknowledgement()

                elif recvFrame.type == FrameType.MSG:
                    try:
                        self.view.displayMessage(f"{recvFrame.user}:{recvFrame.data.decode('utf-8')}")
                    except UnicodeDecodeError:
                        self.view.displayMessage(f"{recvFrame.user}:{recvFrame.data}")
                    self.sendAcknowledgement()

                elif recvFrame.type == FrameType.FILE:
                    if recvFrame.user != self.clientName:
                        uploadDir = "downloads\\" + self.clientName
                        if not os.path.exists(uploadDir):
                            os.makedirs(uploadDir)
                        with open(uploadDir + "\\" + recvFrame.fileName, "a+b") as f:
                            f.write(recvFrame.data)

                elif recvFrame.type == FrameType.HELLO_REQ:
                    if recvFrame.user != self.clientName:
                        # print(f"received a hello request from {recvFrame.user}, sending my hello")
                        self.publishPublicKey()
                    else:
                        # print("received my own hello request frame")
                        pass

                elif recvFrame.type == FrameType.HELLO:
                    if recvFrame.user != self.clientName:
                        self.recipientPublicKey = recvFrame.data
                        self.recipientName = recvFrame.user
                        # print(f"{self.recipientName} introduced themselves with {self.recipientPublicKey} key")
                    else:
                        # print("received my own hello frame")
                        pass

                elif recvFrame.type == FrameType.SESSION_KEY:
                    if recvFrame.user != self.clientName:
                        private, _ = self.keyController.getKeys()
                        self.keyController.lastSessionKey = self.keyController.decryptSessionKey(recvFrame.data, private)
                        # print(f"received session key from {recvFrame.user}")
            except:
                try:
                    self.stopCommunication()
                except OSError:
                    print("An error occurred!")
                break

    def sendMessage(self, msg):
        if self.view is None:
            print("Chat view isn't assigned!")
            return

        self.sendFrame(Frame(FrameType.MSG, msg, self.clientName, mode=self.cipherMode))

    def sendAcknowledgement(self):
        if self.view is None:
            print("Chat view isn't assigned!")
            return

        self.sendFrame(Frame(FrameType.ACK, self.clientName, self.clientName))

    def sendFile(self, path):
        if self.view is None:
            print("Chat view isn't assigned!")
            return
        filesize = os.path.getsize(path)
        self.sendFrame(Frame(FrameType.FILE, b"", self.clientName, os.path.basename(path), mode=self.cipherMode))
        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {os.path.basename(path)}", unit="B", unit_scale=True, unit_divisor=BUFFER_SIZE)
        progressBarPopup = Toplevel()
        progressBarPopup.geometry('50x80')
        Label(progressBarPopup, text="Files are being sent").grid(row=0, column=0)
        barProgress = 0
        progress_var = DoubleVar()
        progress_bar = ttk.Progressbar(progressBarPopup, variable=progress_var, maximum=int(filesize))
        progress_bar.grid(row=1, column=0)
        progressBarPopup.pack_slaves()
        with open(path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break

                self.sendFrame(Frame(FrameType.FILE, bytes_read, self.clientName, os.path.basename(path), mode=self.cipherMode))
                progress.update(len(bytes_read))
                progressBarPopup.update()
                barProgress += BUFFER_SIZE
                progress_var.set(barProgress)
        self.sendFrame(Frame(FrameType.FILE_END, b"", self.clientName, os.path.basename(path), mode=self.cipherMode))

    def sendSessionKey(self, sessionKeyLength):
        sessionKey = self.keyController.generateSessionKey(sessionKeyLength)
        self.keyController.lastSessionKey = sessionKey
        encryptedSessionKey = self.keyController.encryptSessionKey(sessionKey, self.recipientPublicKey)

        self.sendFrame(Frame(FrameType.SESSION_KEY, encryptedSessionKey, self.clientName))

        return sessionKey

    def sendFrame(self, frame):
        if frame.type == FrameType.MSG or frame.type == FrameType.FILE or frame.type == FrameType.FILE_END:
            sessionKey = self.sendSessionKey(32)

            encryptedData = self.keyController.encryptData(frame.data, sessionKey, self.cipherMode)
            frame.data = encryptedData
            # print("data has been encrypted")

        dataFrame = frame.serialize()
        sizeFrame = Frame(FrameType.SIZE, struct.pack('I', len(dataFrame))).serialize()
        self.s.sendall(sizeFrame)
        self.s.sendall(dataFrame)
        # print(f"{frame.type} has been sent")

    def addView(self, view):
        self.view = view
