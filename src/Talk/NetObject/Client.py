import socket
import time
from ..Command import Commands

class Client:
    def __init__(self):
        pass
    def ConnectClient(self, HOST, PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b"Hello, world")

class SleepyClient:
    def __init__(self, sleeptime):
        self.sleeptime = sleeptime
    def ConnectClient(self, HOST, PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                while True:
                    s.send(b"Hello, world")
                    time.sleep(self.sleeptime)
            except KeyboardInterrupt:
                s.close()

class CommandClient:
    def __init__(self, name):
        self.name = name
    def ConnectClient(self, HOST, PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                s.sendall(b"<CONNECTED>")
                time.sleep(0.1)
                s.sendall(self.name)
                data = ""
                while len(data) == 0:
                    data = s.recv(1024).decode()
                if data != "<WELCOME " + self.name.decode() + ">":
                    error = "SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data
                    raise Exception(error)
                commands = []
                while True:
                    command = s.recv(1024).decode()
                    if command == "<END>" or command == "<END><END>":
                        s.sendall(b"<END_RECIEVED>")
                        while command != "<START_JOB>":
                            command = s.recv(1024).decode()
                        Command = Commands.Command(commands)
                        while Command.RunNext():
                            pass
                        print("JOBDONE")
                        s.sendall(b"<DONE_JOB>")
                        print(Command.stdout)
                        commands = []
                    else:
                        commands.append(command)
                        print(f"RECIEVED {command}")
            except KeyboardInterrupt:
                s.close()