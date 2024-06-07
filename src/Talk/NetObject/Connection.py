import socket

class Connection:
    def __init__(self, connection, address, name=""):
        self.connection = connection
        self.address = address
        self.name = name
        self.isbusy = False
    def SetTimeout(self, timeout):
        self.connection.settimeout(timeout)
    def Recieve(self, amount):
        return self.connection.recv(amount)
    def RecieveAll(self):
        bytes = bytearray()
        while True:
            data = self.connection.recv(1024)
            if not data:
                break
            else:
                bytes.extend(data)
        return bytes
    def Send(self, data):
        self.connection.sendall(data)
    def SendFile(self, filename):
        file = open(filename, "r")
        data = file.read(65536)
        count = 0
        while data:
            count += 1
            self.connection.sendall(data.encode("utf-8"))
            data = file.read(65536)
        self.connection.send("<EOF>")
    def EndConnection(self):
        self.connection.close()