import socket
import time
import os
from ..Threading import Threading
from ..NetObject import Connection
from ..Objects import Data
from ..Command import Commands
    

class StatusWorkerServer:
    def __init__(self, connection):
        self.connection = connection
        self.name = connection.name
    def Update(self):
        try:
            self.connection.Send(b"<UPDATE>")
        except ConnectionResetError:
            return
        except ConnectionAbortedError:
            return
    def StatusRequest(self):
        try:
            self.connection.Send({"message" : "<GIVE_STATUS>"})
            self.connection.SetTimeout(5)
            msg = self.connection.Recieve(1024).decode()
            if msg[-10:] != "<OK_START>":
                if msg == "":
                    raise ConnectionResetError()
                raise Exception("RECEIVED INCORRECT RESPONSE")
            total = 0
            for i in range(10):
                self.connection.Send(b"<PING>")
                start = time.time()
                msg = self.connection.Recieve(1024).decode()
                if msg != "<PONG>":
                    if msg == "":
                        raise ConnectionResetError()
                    raise Exception("RECEIVED INCORRECT RESPONSE")
                total += (time.time() - start) / 10
            total *= 1000
            start = time.time()
            self.connection.Send(b"*" * 10000000)
            end = time.time() - start
            uploadspeed = (10000000 / (1024 * 1024)) / end
            self.connection.Send(b"<EOF>")
            msg = self.connection.Recieve(1024).decode()
            self.connection.SetTimeout(None)
            if msg == "<BUSY>":
                return total, uploadspeed, True, True
            if msg == "<IDLE>":
                return total, uploadspeed, True, False
            elif msg == "":
                raise ConnectionResetError()
            raise Exception("RECEIVED INCORRECT RESPONSE")
        except ConnectionResetError:
            return 0, 0, False, False
        except ConnectionAbortedError:
            return 0, 0, False, False
        except TimeoutError:
            return 0, 0, False, False
        except ZeroDivisionError:
            return 0, 0, False, False

@Threading.classthreaded
class StatusWorkerClient:
    def __init__(self, HOST, PORT, name, id, client, commandlist):
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
        message = {"id" : str(self.id)}
        s.sendall(Data.Data(message).Encode())
        data = Data.Data(s.recv(1024)).Decode()
        if data["message"] != "<VALID>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        message = {"type" : "<STATUS_WORKER>"}
        s.sendall(Data.Data(message).Encode())
        print("WORKER CONNECTED")
        self.connection = Connection.Connection(s, HOST)
        self.name = name
        self.commandlist = commandlist
    def Run(self):
        while True:
            message = self.connection.Recieve(1024)
            if message["message"] == "<GIVE_STATUS>":
                print("GIVING STATUS")
                self.connection.connection.sendall(b"<OK_START>")
                for i in range(10):
                    if self.connection.connection.recv(1024).decode() != "<PING>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    self.connection.connection.sendall(b"<PONG>")
                data = ""
                while True:
                    data = self.connection.connection.recv(4096)
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