import socket

class Connection:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
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
    def EndConnection(self):
        self.connection.close()