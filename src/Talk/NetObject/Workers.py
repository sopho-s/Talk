import socket
import time
import os
from ..Threading import Threading
from ..NetObject import Connection

class Worker:
    def __init__(self, connection):
        self.connection = connection
        self.name = connection.name
    def Run(self):
        pass
    

class StatusWorkerServer(Worker):
    def __init__(self, connection):
        super().__init__(connection)
    def StatusRequest(self):
        self.connection.Send(b"<GIVE_STATUS>")
        self.connection.SetTimeout(10)
        if self.connection.Recieve(1024).decode() != "<OK_START>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        total = 0
        for i in range(10):
            self.connection.Send(b"<PING>")
            start = time.time()
            if self.connection.Recieve(1024).decode() != "<PONG>":
                raise Exception("RECEIVED INCORRECT RESPONSE")
            total += (time.time() - start) / 10
        total *= 1000
        start = time.time()
        self.connection.SendFile(os.path.dirname(os.path.abspath(__file__)) + "\\Payload.csv")
        end = time.time() - start
        filestats = os.stat(os.path.dirname(os.path.abspath(__file__)) + "\\Payload.csv")
        uploadspeed = (filestats.st_size / (1024 * 1024)) / end
        self.connection.Send(b"<EOF>")
        if self.connection.Recieve(1024).decode() != "<OK_READY>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        self.connection.SetTimeout(None)
        return total, uploadspeed

@Threading.classthreaded
class StatusWorkerClient(Worker):
    def __init__(self, HOST, PORT, name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                while True:
                    try:
                        s.connect((HOST, PORT))
                        break
                    except:
                        time.sleep(1)
                print("TEST")
                s.sendall(b"<CONNECTED>" + name)
                print("TEST4")
                data = ""
                while len(data) == 0:
                    data = s.recv(1024).decode()
                if data != "<WELCOME " + name + ">":
                    raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
                print("TEST4")
                s.sendall(b"<STATUS_WORKER>")
                print("WORKER CONNECTED")
            except:
                os._exit(1)
            Connection.Connection(s, HOST, name)
        super().__init__(connection)
    def Run(self):
        self.connection.Send(b"<OK_START>")
        for i in range(10):
            if self.connection.Recieve(1024).decode() != "<PING>":
                raise Exception("RECEIVED INCORRECT RESPONSE")
            self.connection.Send(b"<PONG>")
        data = ""
        while True:
            data = self.connection.Recieve(4096)
            if data[-5:] == b"<EOF>":
                break
        self.connection.Send(b"<OK_READY>")