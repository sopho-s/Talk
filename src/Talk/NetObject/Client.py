import socket
import time
import os
from ..Command import Commands
from ..NetObject import Workers, Connection
from ..Objects import Data, Queue
from ..Encryption import *
from ..Threading import Threading
from ..Sanitise import *

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
        self.checksum = 1718209941
        self.name = name
        self.workerthread = None
        self.workerobject = None
        self.isbusy = None
        self.commands = commands
        self.connection = None
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
    def EstablishConnection(self, HOST, PORT, clienttype):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            if data["checksum"] > self.checksum:
                Command = Commands.Command(["<UPDATE>"], self.commands)
                try:
                    while Command.RunNext():
                        pass
                except Exception:
                    print("PERFORMING CLIENT RESET")
                    os._exit(1)
            e = data["keys"][0]
            n = data["keys"][1]
            key1, key2, key3, key4 = EncryptionKeyGen()
            connection = Connection.Connection(s, HOST, self.name, key1, key2, key3, key4)
            key1list, key2list, key3list, key4list = self.GenerateKeyLists(key1, key2, key3, key4)
            message = {"key1" : [EncryptRSA(keyval, e, n) for keyval in key1list], "key2" : [EncryptRSA(keyval, e, n) for keyval in key2list], "key3" : [EncryptRSA(keyval, e, n) for keyval in key3list], "key4" : [EncryptRSA(keyval, e, n) for keyval in key4list]}
            message["checksum"] = self.checksum
            s.sendall(Data.Data(message).Encode())
            data = connection.Recieve(1024)
            print(data)
            if data["message"] != "<VALID>":
                raise Exception("RECEIVED INCORRECT RESPONSE")
            message = {"type" : "<" + clienttype + ">"}
            connection.Send(message)
            print(clienttype + " CONNECTED")
            self.connection = connection
        except KeyboardInterrupt:
            os._exit(1)
        except ConnectionResetError:
            print("CONNECTION CLOSED")
            os._exit(1)
    def Reset(self, s):
        s.close()
        print("PERFORMING CLIENT RESET")
        os._exit(1)
    def ConnectClient(self, HOST, PORT):
        self.EstablishConnection(HOST, PORT, "CLIENT")
        try:
            self.workerthread, self.workerobject = Workers.StatusWorkerClient(HOST, PORT, self.name.decode(), self.id, self, self.commands)
            while True:
                commands = self.connection.RecieveAll()
                print(f"RECIEVED {commands}")
                self.isbusy = True
                self.connection.Send({"message" : "<READY>"})
                if self.connection.Recieve(1024)["message"] != "<START_JOB>":
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                Command = Commands.Command(commands["commands"], self.commands)
                try:
                    while Command.RunNext():
                        pass
                except Exception:
                    self.Reset(s)
                print("JOBDONE")
                self.connection.Send({"message" : "<DONE_JOB>"})
                if self.connection.Recieve(1024)["message"] != "<GET_OUTPUT>":
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                self.connection.Send({"output" : Command.stdout}, True)
                commands = {}
                self.isbusy = False
        except KeyboardInterrupt:
            os._exit(1)
        except ConnectionResetError:
            print("CONNECTION CLOSED")
            os._exit(1)

class RequestClient(CommandClient):
    def __init__(self, name, commands, id, key=None):
        super().__init__(name, commands, id, key)
        self.requests = Queue.CircularQueue(10)
    @Threading.threaded
    def ConnectClient(self, HOST, PORT):
        self.EstablishConnection(HOST, PORT, "USER")
        try:
            while True:
                if self.requests.count != 0:
                    request = self.requests.DeQueue().get("1.0","end").split("\n")
                    self.connection.Send({"message" : request, "statusupdate" : False}, True)
                    message = self.connection.Recieve(1024)
                    print(message)
                    if message["message"] != "<OK>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                else:
                    time.sleep(0.05)
        except KeyboardInterrupt:
            os._exit(1)
        except ConnectionResetError:
            print("CONNECTION CLOSED")
            os._exit(1)