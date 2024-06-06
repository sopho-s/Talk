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
        error = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                while True:
                    try:
                        s.connect((HOST, PORT))
                        break
                    except:
                        time.sleep(1)
                        print("WAITING")
                print("CONNECTED")
                s.sendall(b"<CONNECTED>" + self.name)
                data = ""
                while len(data) == 0:
                    data = s.recv(1024).decode()
                if data != "<WELCOME " + self.name.decode() + ">":
                    error = "SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data
                    raise Exception(error)
                commands = []
                while True:
                    command = s.recv(1024).decode()
                    print(f"RECIEVED {command}")
                    s.sendall(b"<COMMAND_RECIEVED>")
                    if command == "<END>" or command == "<END><END>":
                        s.sendall(b"<END_RECIEVED>")
                        while command != "<START_JOB>":
                            command = s.recv(1024).decode()
                        Command = Commands.Command(commands)
                        try:
                            while Command.RunNext():
                                pass
                        except Exception:
                            s.close()
                            print("PERFORMING CLIENT RESET")
                            break
                        print("JOBDONE")
                        s.sendall(b"<DONE_JOB>")
                        while s.recv(1024).decode() != "<GET_OUTPUT>":
                            pass
                        for i in range(len(Command.stdout)):
                            s.sendall(str(len(Command.stdout)).encode('utf-8'))
                            while s.recv(1024).decode() != "<NEXT_OUTPUT>":
                                pass
                        s.sendall(b"<OUTPUT_DONE>")
                        commands = []
                    else:
                        commands.append(command)
            except KeyboardInterrupt:
                s.close()
            except ConnectionResetError:
                print("CONNECTION CLOSED")
                raise Exception("STOP")