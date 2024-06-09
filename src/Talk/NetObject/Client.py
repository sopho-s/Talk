import socket
import time
import os
from ..Command import Commands
from ..NetObject import Workers
from ..Objects import Data

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
    def __init__(self, name, commands, id, key=None):
        self.name = name
        self.workerthread = None
        self.workerobject = None
        self.isbusy = None
        self.commands = commands
        self.id = id
        self.key = key
    def ConnectClient(self, HOST, PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                while True:
                    try:
                        s.connect((HOST, PORT))
                        break
                    except:
                        time.sleep(1)
                message = {"message" : "<CONNECTED>", "name" : self.name.decode()}
                s.sendall(Data.Data(message).Encode())
                data = ""
                while len(data) == 0:
                    data = Data.Data(s.recv(1024)).Decode()
                if data["message"] != "<WELCOME>" or data["name"]  != self.name.decode():
                    raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
                message = {"id" : str(self.id)}
                s.sendall(Data.Data(message).Encode())
                data = Data.Data(s.recv(1024)).Decode()
                if data["message"] != "<VALID>":
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                message = {"type" : "<CLIENT>"}
                s.sendall(Data.Data(message).Encode())
                print("CLIENT CONNECTED")
                self.workerthread, self.workerobject = Workers.StatusWorkerClient(HOST, PORT, self.name.decode(), self.id, self, self.commands)
                commands = []
                while True:
                    command = s.recv(1024).decode()
                    print(f"RECIEVED {command}")
                    if command == "<END>" or command == "<END><END>":
                        self.isbusy = True
                        s.sendall(b"<END_RECIEVED>")
                        if s.recv(1024).decode() != "<START_JOB>":
                            raise Exception("RECEIVED INCORRECT RESPONSE")
                        Command = Commands.Command(commands, self.commands)
                        try:
                            while Command.RunNext():
                                pass
                        except Exception:
                            s.close()
                            print("PERFORMING CLIENT RESET")
                            os._exit(1)
                        print("JOBDONE")
                        s.sendall(b"<DONE_JOB>")
                        if s.recv(1024).decode() != "<GET_OUTPUT>":
                            raise Exception("RECEIVED INCORRECT RESPONSE")
                        for command in Command.stdout:
                            s.sendall(command.encode('utf-8'))
                            s.sendall(b"<EOSTDO>")
                            msg = s.recv(1024).decode()
                            if msg != "<NEXT_OUTPUT>":
                                raise Exception("RECEIVED INCORRECT RESPONSE")
                        s.sendall(b"<OUTPUT_DONE>")
                        commands = []
                        self.isbusy = False
                    elif command != "<NEXT_OUTPUT>":
                        s.sendall(b"<COMMAND_RECIEVED>")
                        commands.append(command)
            except KeyboardInterrupt:
                os._exit(1)
            except ConnectionResetError:
                print("CONNECTION CLOSED")
                os._exit(1)