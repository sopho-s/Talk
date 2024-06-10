import socket
import time
from ..Objects import Data
from ..Encryption import *

class Connection:
    def __init__(self, connection, address, name="", key1 = 0, key2 = 0, key3 = 0, key4 = 0):
        self.connection = connection
        self.address = address
        self.name = name
        self.isbusy = False
        self.isonline = True
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
        self.key4 = key4
    def CheckOnline(self):
        try:
            self.connection.sendall(b"<ONLINE?>")
            data = self.connection.recv(1024)
            if not data.decode() == "":
                self.isonline = True
                return True
        except ConnectionAbortedError:
            pass
        except ConnectionResetError:
            pass
        self.isonline = False
        return False
    def SetTimeout(self, timeout):
        self.connection.settimeout(timeout)
    def Recieve(self, amount):
        return Data.Data(Decrypt(self.connection.recv(amount).decode("utf-8"), self.key1, self.key2, self.key3, self.key4).encode("utf-8")).Decode()
    def RecieveAll(self):
        bytes = bytearray()
        while True:
            data = self.connection.recv(1024)
            print(data)
            if data[-1] == b"\x00":
                bytes.extend(data[:-1])
                break
            else:
                bytes.extend(data)
        return Data.Data(Decrypt(bytes.decode("utf-8"), self.key1, self.key2, self.key3, self.key4).encode("utf-8")).Decode()
    def Send(self, data, withnull = False):
        self.connection.sendall(Encrypt(Data.Data(data).Encode().decode("utf-8"), self.key1, self.key2, self.key3, self.key4).encode("utf-8"))
        if withnull:
            self.connection.sendall(b"\x00")
    def SendFile(self, filename):
        file = open(filename, "r")
        data = file.read(4096)
        while data:
            self.connection.sendall(Encrypt(Data.Data(data).Encode().decode("utf-8"), self.key1, self.key2, self.key3, self.key4).encode("utf-8"))
            data = file.read(4096)
    def EndConnection(self):
        self.connection.close()