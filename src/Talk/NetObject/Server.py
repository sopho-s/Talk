import socket
import time
import threading
from ..NetObject import Connection
from ..Threading import Threading
from ..Objects import Queue

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

class MultiConnSingleInstructionServerWithCommands(MultiConnServer):
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
        self.commands = []
        self.commandlock = threading.Lock()
        self.commandhandler = None
        self.connectionqueue = Queue.CircularQueue(10)
        self.shutdown = False
    @Threading.threaded
    def StartServer(self):
        self.commandhandler = self.CommandHandler()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.HOST, self.PORT))
                while True:
                    if self.shutdown:
                        s.close()
                        self.commandhandler.raise_exception()
                        self.commandhandler.join()
                        return
                    s.listen()
                    conn, addr = s.accept()
                    data = ""
                    while len(data) == 0:
                        data = conn.recv(1024).decode()
                    if data[0:11] == "<CONNECTED>":
                        objconn = Connection.Connection(conn, addr, data[11:])
                        objconn.Send(b"<WELCOME " + objconn.name.encode('utf-8') + b">")
                        self.connectionqueue.EnQueue(objconn)
                    else:
                        conn.sendall(b"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, THUS CONNECTION WILL BE TERMINATED")
                        conn.close()  
                        print(f"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, INSTEAD GOT {data[0:11]}")
            except KeyboardInterrupt:
                s.close()
    @Threading.threaded
    def CommandHandler(self):
        while True:
            if self.connectionqueue.count != 0 and len(self.commands) > 0:
                commands = []
                with self.commandlock:
                    commands = self.commands.pop(0)
                try:
                    connection = self.connectionqueue.DeQueue()
                    while connection == False:
                        time.sleep(0.1)
                        connection = self.connectionqueue.DeQueue()
                        print(self.connectionqueue.count)
                    for command in commands:
                        connection.Send(command.encode("utf-8"))
                        while connection.Recieve(1024).decode() != "<COMMAND RECIEVED>":
                            pass
                    connection.Send(b"<END>")
                    while connection.Recieve(1024).decode() != "<END_RECIEVED>":
                        pass
                    connection.Send(b"<START_JOB>")
                    while connection.Recieve(1024).decode() != "<DONE_JOB>":
                        pass
                    connection = self.connectionqueue.EnQueue(connection)
                except KeyboardInterrupt:
                    connection.Send(b"<STOP_JOB>")
                    while connection.Recieve() != "<JOB_STOPPED>":
                        pass
                    connection.Send(b"<QUIT_JOB>")
                    while connection.Recieve() != "<JOB_QUIT>":
                        pass
                    break
                    