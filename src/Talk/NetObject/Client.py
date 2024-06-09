import socket
import time
import os
from ..Command import Commands
from ..NetObject import Workers, Connection
from ..Objects import Data
from ..Encryption import *

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
                e = data["keys"][0]
                n = data["keys"][1]
                print(e)
                print(n)
                key1, key2, key3, key4 = EncryptionKeyGen()
                #print(key1)
                #print(key2)
                #print(key3)
                #print(key4)
                message = {"keys" : [EncryptRSA(key1, e, n), EncryptRSA(key2, e, n), EncryptRSA(key3, e, n), EncryptRSA(key4, e, n)]}
                s.sendall(Data.Data(message).Encode())
                connection = Connection.Connection(s, HOST, self.name, key1, key2, key3, key4)
                data = connection.Recieve(1024)
                if data["message"] != "<VALID>":
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                message = {"type" : "<CLIENT>"}
                connection.Send(message)
                print("CLIENT CONNECTED")
                if data["message"] != "<VALID>":
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                message = {"type" : "<CLIENT>"}
                connection.Send(message)
                print("CLIENT CONNECTED")
                self.workerthread, self.workerobject = Workers.StatusWorkerClient(HOST, PORT, self.name.decode(), self.id, self, self.commands)
                while True:
                    commands = connection.RecieveAll()
                    print(f"RECIEVED {commands}")
                    self.isbusy = True
                    connection.Send({"message" : "<READY>"})
                    if connection.Recieve(1024)["message"] != "<START_JOB>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    Command = Commands.Command(commands["commands"], self.commands)
                    try:
                        while Command.RunNext():
                            pass
                    except Exception:
                        s.close()
                        print("PERFORMING CLIENT RESET")
                        os._exit(1)
                    print("JOBDONE")
                    connection.Send({"message" : "<DONE_JOB>"})
                    if connection.Recieve(1024)["message"] != "<GET_OUTPUT>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send({"output" : Command.stdout}, True)
                    commands = {}
                    self.isbusy = False
            except KeyboardInterrupt:
                os._exit(1)
            except ConnectionResetError:
                print("CONNECTION CLOSED")
                os._exit(1)