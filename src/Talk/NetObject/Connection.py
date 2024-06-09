import socket
from ..Objects import Data

class Connection:
    def __init__(self, connection, address, name=""):
        self.connection = connection
        self.address = address
        self.name = name
        self.isbusy = False
        self.isonline = True
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
        return Data.Data(self.connection.recv(amount)).Decode()
    def RecieveAll(self):
        bytes = bytearray()
        while True:
            data = self.connection.recv(1024)
            if data == b"":
                break
            else:
                bytes.extend(data)
        print(bytes)
        return Data.Data(bytes).Decode()
    def Send(self, data, withnull = False):
        self.connection.sendall(Data.Data(data).Encode())
        if withnull:
            self.connection.sendall(b"")
    def SendFile(self, filename):
        file = open(filename, "r")
        data = file.read(4096)
        while data:
            self.connection.sendall(data.encode("utf-8"))
            data = file.read(4096)
    def EndConnection(self):
        self.connection.close()