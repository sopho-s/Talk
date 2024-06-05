import socket
import time
from ..NetObject import Connection
from ..Threading import Threading

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
    def StartServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            while True:
                s.listen()
                conn, addr = s.accept()
                objconn = Connection.Connection(conn, addr)
                with conn:
                    print(f"Connected by {addr}")
                    print(objconn.RecieveAll())
                        
class MultiConnServer(Server):
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
    def StartServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            while True:
                s.listen()
                conn, addr = s.accept()
                objconn = Connection.Connection(conn, addr)
                self.PrintData(objconn)
    @Threading.threaded
    def PrintData(self, connection):
        while True:
            print(f"Connected by {connection.address}")
            data = connection.Recieve(1024)
            if len(data) == 0:
                break
            else:
                print(data)

class SleepyMultiConnServer(MultiConnServer):
    def __init__(self, HOST, PORT, sleeptime):
        super().__init__(HOST, PORT)
        self.sleeptime = sleeptime
    @Threading.threaded
    def PrintData(self, connection):
        while True:
            print(f"Connected by {connection.address}")
            data = connection.Recieve(1024)
            if len(data) == 0:
                break
            else:
                print(data)
            time.sleep(self.sleeptime)