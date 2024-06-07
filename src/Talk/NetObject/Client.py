import socket
import time
import os
from ..Command import Commands
from ..NetObject import Workers

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
                while True:
                    try:
                        s.connect((HOST, PORT))
                        break
                    except:
                        time.sleep(1)
                s.sendall(b"<CONNECTED>" + self.name)
                data = ""
                while len(data) == 0:
                    data = s.recv(1024).decode()
                if data != "<WELCOME " + self.name.decode() + ">":
                    raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
                s.sendall(b"<CLIENT>")
                Workers.StatusWorkerClient(HOST, PORT, self.name.decode())
                commands = []
                while True:
                    command = s.recv(1024).decode()
                    if command != "<GIVE_STATUS>":
                        print(f"RECIEVED {command}")
                        if command == "<END>" or command == "<END><END>":
                            s.sendall(b"<END_RECIEVED>")
                            if s.recv(1024).decode() != "<START_JOB>":
                                raise Exception("RECEIVED INCORRECT RESPONSE")
                            Command = Commands.Command(commands)
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
                                if s.recv(1024).decode() != "<NEXT_OUTPUT>":
                                    raise Exception("RECEIVED INCORRECT RESPONSE")
                            s.sendall(b"<OUTPUT_DONE>")
                            commands = []
                        else:
                            s.sendall(b"<COMMAND_RECIEVED>")
                            commands.append(command)
            except KeyboardInterrupt:
                os._exit(1)
            except ConnectionResetError:
                print("CONNECTION CLOSED")
                os._exit(1)