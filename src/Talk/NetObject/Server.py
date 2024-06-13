import socket
import time
import threading
import tkinter as tk
import os
from ..NetObject import Connection
from ..NetObject import Workers
from ..Threading import Threading
from ..Command import Commands
from ..Objects import Queue, Data
from ..Encryption import *

class StatusWidgit:
    def __init__(self, widgit, objconn):
        self.ping = None
        self.uploadspeed = None
        self.online = True
        self.busy = True
        self.widgit = tk.Toplevel(widgit)
        self.widgit.geometry("200x200")
        self.name = objconn.name
        self.namewidgit = tk.Label(self.widgit, text=objconn.name)
        self.pingwidgit = tk.Label(self.widgit, text="")
        self.uploadspeedwidgit = tk.Label(self.widgit, text="")
        self.onlinewidgit = tk.Label(self.widgit, text="")
        self.busywidgit = tk.Label(self.widgit, text="")
        self.widgit.grid_columnconfigure(0, weight=1)
        self.namewidgit.grid_columnconfigure(0, weight=1)
        self.pingwidgit.grid_columnconfigure(1, weight=1)
        self.uploadspeedwidgit.grid_columnconfigure(2, weight=1)
        self.onlinewidgit.grid_columnconfigure(3, weight=1)
        self.busywidgit.grid_columnconfigure(4, weight=1)
        self.namewidgit.grid(row=0)
        self.pingwidgit.grid(row=1)
        self.uploadspeedwidgit.grid(row=2)
        self.onlinewidgit.grid(row=3)
        self.busywidgit.grid(row=4)
class Server:
<<<<<<< HEAD
    def __init__(self, HOST, PORT, commands, widgit = None, maxslaves = 10, key=None):
        self.checksum = 1718293696
=======
    def __init__(self, HOST, PORT, widgit, key=None):
        self.checksum = 1718293696
>>>>>>> 4b6b23da5ae37303fd313d785e44ebd1f0656ff7
        self.HOST = HOST
        self.PORT = PORT
        self.widgit = widgit
        self.statusupdate = False
        self.statuswidgits = []
        self.statusworkers = []
        self.statushandler = []
        self.userthreads = []
        self.macrolist = commands
        self.commands = []
        self.commandlock = threading.Lock()
        self.commandhandler = None
        self.connectionqueue = Queue.CircularQueue(10)
        self.update = False
        self.shutdown = False
        self.printlock = threading.Lock()
        self.acceptall = True
        self.connectedids = []
        self.keys = [0, 0, 0, 0]
        self.e, self.d, self.n = RSA()
    def AddUser(self, type, connection):
        if type == "<CLIENT>":
            print("NEW CLIENT CONNECTED")
            self.connectionqueue.EnQueue(connection)
        elif type == "<STATUS_WORKER>":
            print("NEW STATUS WORKER CONNECTED")
            if not any(statuswidgit.name == connection.name for statuswidgit in self.statuswidgits):
                if self.widgit != None:
                    newstatuswidgit = StatusWidgit(self.widgit, connection)
                    self.statuswidgits.append(newstatuswidgit)
                self.statusworkers.append(Workers.StatusWorkerServer(connection))
            else:
                for worker in self.statusworkers:
                    if worker.name == connection.name:
                        worker.connection = connection
            self.statusupdate = True
        elif type == "<USER>":
            print("NEW USER CONNECTED")
            self.userthreads.append(self.UserHandler(connection))
    @Threading.threaded
    def StartServer(self):
        self.statushandler = self.StatusHandler()
        self.commandhandler = self.CommandHandler()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.HOST, self.PORT))
                while True:
                    s.listen()
                    conn, addr = s.accept()
                    data = ""
                    while len(data) == 0:
                        data = Data.Data(conn.recv(1024)).Decode()
                    if data["message"] == "<CONNECTED>":
                        print("CONNECTION ESTABLISHING")
                        message = {}
                        message["message"] = "<WELCOME>"
                        message["name"] = data["name"]
                        message["checksum"] = self.checksum
                        name = data["name"]
                        message["keys"] = [self.e, self.n]
                        conn.sendall(Data.Data(message).Encode())
                        data = Data.Data(conn.recv(1024)).Decode()
                        if data["checksum"] > self.checksum:
                            Command = Commands.Command(["<UPDATE>"], self.macrolist)
                            try:
                                while Command.RunNext():
                                    pass
                            except Exception:
                                print("PERFORMING CLIENT RESET")
                                os._exit(1)
                        key1 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key1"])]))
                        key2 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key2"])]))
                        key3 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key3"])]))
                        key4 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key4"])]))
                        objconn = Connection.Connection(conn, addr, name, key1, key2, key3, key4)
                        if self.acceptall:
                            objconn.Send({"message" : "<VALID>"})
                        data = objconn.Recieve(1024)
                        print(data)
                        self.AddUser(data["type"], objconn)
                    else:
                        conn.sendall(Data.Data({"message" : "CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, THUS CONNECTION WILL BE TERMINATED"}).Encode())
                        conn.close()  
                        print(f"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, INSTEAD GOT {data["name"]}")
            except KeyboardInterrupt:
                s.close()
    @Threading.threaded
    def RecieveCommand(self, connection):
        message = connection.Recieve(1024)
        if message["message"] != "<DONE_JOB>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        connection.Send({"message" : "<GET_OUTPUT>"})
        output = connection.RecieveAll()
        print(output)
        with self.printlock:
            for out in output["output"]:
                print(out)
                print("\n\n")
        with self.commandlock:
            connection = self.connectionqueue.EnQueue(connection)
    @Threading.threaded
    def CommandHandler(self):
        while True:
            shouldberestored = True
            if self.connectionqueue.count != 0 and len(self.commands) > 0:
                commands = []
                with self.commandlock:
                    commands = self.commands.pop(0)
                try:
                    connection = self.connectionqueue.DeQueue()
                    while connection == False:
                        time.sleep(0.1)
                        connection = self.connectionqueue.DeQueue()
                    connection.Send({"commands" : commands, "command_amount" : len(commands)}, True)
                    if connection.Recieve(1024)["message"] != "<READY>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send({"message" : "<START_JOB>"})
                    if shouldberestored:
                        self.RecieveCommand(connection)
                except KeyboardInterrupt:
                    break
            else:
                time.sleep(0.05)
    @Threading.threaded
    def StatusHandler(self):
        while True:
            if self.update:
                for worker in self.statusworkers:
                    worker.Update()
                self.update = False
            if self.statusupdate:
                print("REQUESTING STATUS")
                for worker in self.statusworkers:
                    ping, uploadspeed, online, isbusy = worker.StatusRequest()
                    if self.widgit != None:
                        currentwidgit = None
                        for statuswidgit in self.statuswidgits:
                            if statuswidgit.name == worker.name:
                                currentwidgit = statuswidgit
                                break
                        self.UpdateStatusWidgit(currentwidgit, ping, uploadspeed, online, isbusy)
                self.statusupdate = False
            else:
                time.sleep(0.5)
                self.statusupdate = True
    def UpdateStatusWidgit(self, currentwidgit, ping, uploadspeed, online, isbusy):
        if not online:
            currentwidgit.pingwidgit.config(text=f"Ping: 0ms")
            currentwidgit.uploadspeedwidgit.config(text=f"Upload Speed: 0MBs")
            currentwidgit.onlinewidgit.config(text=f"Offline")
            currentwidgit.onlinewidgit.config(fg="#9e0000")
            return
        else:
            currentwidgit.onlinewidgit.config(text=f"Online")
            currentwidgit.onlinewidgit.config(fg="#00d100")
        currentwidgit.ping = ping
        currentwidgit.pingwidgit.config(text=f"Ping: " + ("%.0f" % ping) + "ms")
        if ping < 10:
            currentwidgit.pingwidgit.config(fg="#00d100")
        elif ping < 40:
            currentwidgit.pingwidgit.config(fg="#99d100")
        elif ping < 100:
            currentwidgit.pingwidgit.config(fg="#e89f00")
        elif ping < 1000:
            currentwidgit.pingwidgit.config(fg="#ff2f00")
        else:
            currentwidgit.pingwidgit.config(fg="#9e0000")
        currentwidgit.uploadspeed = uploadspeed
        currentwidgit.uploadspeedwidgit.config(text=f"Upload Speed: " + ("%.1f" % uploadspeed) + "MBs")
        if uploadspeed < 0.1:
            currentwidgit.uploadspeedwidgit.config(fg="#9e0000")
        elif uploadspeed < 0.5:
            currentwidgit.uploadspeedwidgit.config(fg="#ff2f00")
        elif uploadspeed < 1:
            currentwidgit.uploadspeedwidgit.config(fg="#e89f00")
        elif uploadspeed < 5:
            currentwidgit.uploadspeedwidgit.config(fg="#99d100")
        else:
            currentwidgit.uploadspeedwidgit.config(fg="#00d100")
        currentwidgit.busy = isbusy
        if isbusy:
            currentwidgit.busywidgit.config(text=f"Busy")
            currentwidgit.busywidgit.config(fg="#e89f00")
        else:
            currentwidgit.busywidgit.config(text=f"Idle")
            currentwidgit.busywidgit.config(fg="#00d100")
    @Threading.threaded
    def UserHandler(self, user):
        while True:
            commands = user.RecieveAll()
            user.Send({"message" : "<OK>"})
            if commands["statusupdate"]:
                pass
            else:
                with self.commandlock:
                    self.commands.append(commands["message"])