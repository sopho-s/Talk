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
            if data.decode() == "":
                self.isonline = True
                return True
        except ConnectionAbortedError:
            pass
        except ConnectionResetError:
            pass
        except BrokenPipeError:
            pass
        self.isonline = False
        return False
    def ComplexCheckOnline(self):
        try:
            self.Send({"message" : "<ONLINE?>"}, True)
            data = self.Recieve(1024)
            if data != "":
                self.isonline = True
                return True
        except ConnectionAbortedError:
            pass
        except ConnectionResetError:
            pass
        except BrokenPipeError:
            pass
        self.isonline = False
        return False
    def SetTimeout(self, timeout):
        self.connection.settimeout(timeout)
    def Recieve(self, amount):
        return Data.Data(self.connection.recv(amount).decode("utf-8").encode("utf-8")).Decode()
    def RecieveAll(self):
        bytes = bytearray()
        while True:
            data = self.connection.recv(1024)
            bytes.extend(data)
            if bytes[-5:] == b"\x00\x00\x00\x00\x00":
                bytes = bytes[:-5]
                break
        return Data.Data(bytes.decode("utf-8").encode("utf-8")).Decode()
    def Send(self, data, withnull = False):
        self.connection.sendall(Data.Data(data).Encode().decode("utf-8").encode("utf-8"))
        if withnull:
            self.connection.sendall(b"\x00\x00\x00\x00\x00")
    def SendFile(self, filename):
        file = open(filename, "r")
        data = file.read(4096)
        while data:
            self.connection.sendall(Encrypt(Data.Data(data).Encode().decode("utf-8"), self.key1, self.key2, self.key3, self.key4).encode("utf-8"))
            data = file.read(4096)
    def EndConnection(self):
        self.connection.close()
