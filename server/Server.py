import socket
import threading
from frame.Frame import *
import struct


class Server:
    def __init__(self, addr, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")

        self.s.bind((addr, port))
        print(f"socket bound to port {port}")

        self.s.listen()    
        print("socket is listening")

        self.clients = []
        self.isRunning = True

        self.connectClients()

    def connectClients(self):
        while self.isRunning:
            conn, addr = self.s.accept()
            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
            self.clients.append((conn, addr))
            print(f"New connection from {addr}")

    def handleClient(self, conn, addr):
        connected = True
        default_size = len(Frame(FrameType.SIZE, struct.pack('I', 420)).serialize())
        size = default_size
        while connected:
            # receive message
            message = conn.recv(size)
            recvFrame = pickle.loads(message)
            size = default_size
            packets = []

            if recvFrame.type == FrameType.SIZE:
                size = struct.unpack('I', recvFrame.data)
                size = size[0]
            elif recvFrame.type == FrameType.FILE:
                while True:
                    bytes_read = conn.recv(size)
                    recvFrame = pickle.loads(bytes_read)
                    size = default_size
                    packets.append(bytes_read)
                    if recvFrame.type == FrameType.SIZE:
                        size = struct.unpack('I', recvFrame.data)
                        size = size[0]
                    elif recvFrame.type == FrameType.FILE_END:
                        break
            elif recvFrame.type == FrameType.CLOSE:
                # close the connection
                conn.shutdown(socket.SHUT_WR)
                conn.close()
                self.clients.remove((conn, addr))
                connected = False
                print(f"Client {addr}: {recvFrame.user} disconnected!")
                break

            # broadcast message
            self.broadcastMessage(message)
            for packet in packets:
                self.broadcastMessage(packet)

    def broadcastMessage(self, message):
        for client in self.clients:
            client[0].sendall(message)
            # print(f"sending message to client {client[1]}")


def startServer(addr, port):
    server = Server(addr, port)
