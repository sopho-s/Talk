import socket
import time
import os
from ..Threading import Threading
from ..NetObject import Connection
from ..Objects import Data
from ..Command import Commands
from ..Encryption import *
    

class StatusWorkerServer:
    def __init__(self, connection):
        self.connection = connection
        self.name = connection.name
    def Update(self):
        try:
            self.connection.Send({"message" : "<UPDATE>"})
        except ConnectionResetError:
            return
        except ConnectionAbortedError:
            return
    def StatusRequest(self):
        try:
            self.connection.Send({"message" : "<GIVE_STATUS>"})
            self.connection.SetTimeout(3)
            msg = self.connection.connection.recv(1024).decode()
            if msg[-10:] != "<OK_START>":
                if msg == "":
                    raise ConnectionResetError()
                raise Exception("RECEIVED INCORRECT RESPONSE")
            total = 0
            for i in range(10):
                self.connection.connection.sendall(b"<PING>")
                start = time.time()
                msg = self.connection.connection.recv(1024).decode()
                if msg != "<PONG>":
                    if msg == "":
                        raise ConnectionResetError()
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                total += (time.time() - start) / 10
            total *= 1000
            start = time.time()
            self.connection.connection.sendall(b"*" * 1000000)
            self.connection.connection.sendall(b"<EOF>")
            msg = self.connection.connection.recv(1024).decode()
            end = time.time() - start
            uploadspeed = (1000000 / (1024 * 1024)) / end
            self.connection.SetTimeout(None)
            if msg == "<BUSY>":
                return total, uploadspeed, True, True
            if msg == "<IDLE>":
                return total, uploadspeed, True, False
            elif msg == "":
                raise ConnectionResetError()
            raise Exception("RECEIVED INCORRECT RESPONSE")
        except ConnectionResetError:
            self.connection.connection.send(b" ")
            return 0, 0, False, False
        except ConnectionAbortedError:
            self.connection.connection.send(b" ")
            return 0, 0, False, False
        except TimeoutError:
            self.connection.connection.send(b" ")
            return 0, 0, False, False
        except ZeroDivisionError:
            self.connection.connection.send(b" ")
            return 0, 0, False, False

@Threading.classthreaded
class StatusWorkerClient:
    def __init__(self, HOST, PORT, name, id, client, commandlist):
        self.checksum = 1718053973
        self.client = client
        self.id = id
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.connect((HOST, PORT))
                break
            except:
                time.sleep(1)
        message = {"message" : "<CONNECTED>", "name" : name}
        s.sendall(Data.Data(message).Encode())
        data = ""
        while len(data) == 0:
            data = Data.Data(s.recv(1024)).Decode()
        if data["message"] != "<WELCOME>" or data["name"]  != name:
            raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
        if data["checksum"] != self.checksum:
            Command = Commands.Command(["<UPDATE>"], self.commandlist)
            try:
                while Command.RunNext():
                    pass
            except Exception:
                print("PERFORMING CLIENT RESET")
                os._exit(1)
        e = data["keys"][0]
        n = data["keys"][1]
        key1, key2, key3, key4 = EncryptionKeyGen()
        print(f"key1: {key1}")
        print(f"key2: {key2}")
        print(f"key3: {key3}")
        print(f"key4: {key4}")
        self.connection = Connection.Connection(s, HOST, name, key1, key2, key3, key4)
        key1list, key2list, key3list, key4list = self.GenerateKeyLists(key1, key2, key3, key4)
        message = {"key1" : [EncryptRSA(keyval, e, n) for keyval in key1list], "key2" : [EncryptRSA(keyval, e, n) for keyval in key2list], "key3" : [EncryptRSA(keyval, e, n) for keyval in key3list], "key4" : [EncryptRSA(keyval, e, n) for keyval in key4list]}
        s.sendall(Data.Data(message).Encode())
        data = self.connection.Recieve(1024)
        print(data)
        if data["message"] != "<VALID>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        message = {"type" : "<STATUS_WORKER>"}
        self.connection.Send(message)
        print("STATUS WORKER CONNECTED")
        self.name = name
        self.commandlist = commandlist
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
    def Run(self):
        while True:
            try:
                message = self.connection.Recieve(1024)
                if message["message"] == "<GIVE_STATUS>":
                    print("GIVING STATUS")
                    self.connection.connection.sendall(b"<OK_START>")
                    for i in range(10):
                        if self.connection.connection.recv(1024).decode() != "<PING>":
                            raise Exception("RECEIVED INCORRECT RESPONSE OR CONNECTION ERROR, RETRYING")
                        self.connection.connection.sendall(b"<PONG>")
                    data = ""
                    while True:
                        data = self.connection.connection.recv(4096)
                        if data[-1:] == b" ":
                            raise Exception("CONNECTION ERROR, RETRYING")
                        if data[-5:] == b"<EOF>":
                            break
                    if self.client.isbusy:
                        self.connection.connection.sendall(b"<BUSY>")
                    else:
                        self.connection.connection.sendall(b"<IDLE>")
                elif message["message"] == "<ONLINE?>":
                    self.connection.connection.sendall(b"<ONLINE>")
                elif message["message"] == "<UPDATE>":
                    Command = Commands.Command(["<UPDATE>"], self.commandlist)
                    try:
                        while Command.RunNext():
                            pass
                    except Exception:
                        print("PERFORMING CLIENT RESET")
                        os._exit(1)
                else:
                    time.sleep(0.1)
            except Exception:
                pass