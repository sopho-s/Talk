import socket

class Connection:
    def __init__(self, connection, address, name=""):
        self.connection = connection
        self.address = address
        self.name = name
        self.isbusy = False
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
    def EndConnection(self):
        self.connection.close()