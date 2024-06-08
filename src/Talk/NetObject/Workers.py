import socket
import time
import os
from ..Threading import Threading
from ..NetObject import Connection
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
            self.connection.Send(b"<GIVE_STATUS>")
            self.connection.SetTimeout(10)
            msg = self.connection.Recieve(1024).decode()
            if msg != "<OK_START>":
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
            self.connection.Send(b"*" * 1000000)
            end = time.time() - start
            uploadspeed = (1000000 / (1024 * 1024)) / end
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

@Threading.classthreaded
class StatusWorkerClient:
    def __init__(self, HOST, PORT, name, client, commandlist):
        self.client = client
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.connect((HOST, PORT))
                break
            except:
                time.sleep(1)
        s.sendall(b"<CONNECTED>" + name.encode("utf-8"))
        data = ""
        while len(data) == 0:
            data = s.recv(1024).decode()
        if data != "<WELCOME " + name + ">":
            raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
        self.connection = Connection.Connection(s, HOST, name)
        self.connection.Send(b"<STATUS_WORKER>")
        print("WORKER CONNECTED")
        self.name = name
        self.commandlist = commandlist
    def Run(self):
        while True:
            msg = self.connection.Recieve(1024).decode()
            if msg == "<GIVE_STATUS>":
                print("GIVING STATUS")
                self.connection.Send(b"<OK_START>")
                for i in range(10):
                    if self.connection.Recieve(1024).decode() != "<PING>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    self.connection.Send(b"<PONG>")
                data = ""
                while True:
                    data = self.connection.Recieve(4096)
                    if data[-5:] == b"<EOF>":
                        break
                if self.client.isbusy:
                    self.connection.Send(b"<BUSY>")
                else:
                    self.connection.Send(b"<IDLE>")
            elif msg == "<ONLINE?>":
                self.connection.Send(b"<ONLINE>")
            elif msg == "<UPDATE>":
                Command = Commands.Command(["<UPDATE>"], self.commandlist)
                try:
                    while Command.RunNext():
                        pass
                except Exception:
                    print("PERFORMING CLIENT RESET")
                    os._exit(1)
            else:
                time.sleep(0.1)