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
    def GenerateKeyLists(self, key1, key2, key3, key4):
        key1list = []
        key1 = str(key1)
        while len(key1) > 6:
            key1list.append(int(key1[-6:]))
            key1 = key1[:-6]
        key1list.append(int(key1))
        
        key2list = []
        key2 = str(key2)
        while len(key2) > 6:
            key2list.append(int(key2[-6:]))
            key2 = key2[:-6]
        key2list.append(int(key2))
        
        key3list = []
        key3 = str(key3)
        while len(key3) > 6:
            key3list.append(int(key3[-6:]))
            key3 = key3[:-6]
        key3list.append(int(key3))
        
        key4list = []
        key4 = str(key4)
        while len(key4) > 6:
            key4list.append(int(key4[-6:]))
            key4 = key4[:-6]
        key4list.append(int(key4))
        return key1list, key2list, key3list, key4list
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
                key1, key2, key3, key4 = EncryptionKeyGen()
                print(f"key1: {key1}")
                print(f"key2: {key2}")
                print(f"key3: {key3}")
                print(f"key4: {key4}")
                connection = Connection.Connection(s, HOST, self.name, key1, key2, key3, key4)
                key1list, key2list, key3list, key4list = self.GenerateKeyLists(key1, key2, key3, key4)
                message = {"key1" : [EncryptRSA(keyval, e, n) for keyval in key1list], "key2" : [EncryptRSA(keyval, e, n) for keyval in key2list], "key3" : [EncryptRSA(keyval, e, n) for keyval in key3list], "key4" : [EncryptRSA(keyval, e, n) for keyval in key4list]}
                s.sendall(Data.Data(message).Encode())
                data = connection.Recieve(1024)
                print(data)
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