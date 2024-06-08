import socket
import time
import threading
import tkinter as tk
import os
from ..NetObject import Connection
from ..NetObject import Workers
from ..Threading import Threading
from ..Objects import Queue

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
    def __init__(self, HOST, PORT, widgit):
        self.HOST = HOST
        self.PORT = PORT
        self.widgit = widgit
        self.statusupdate = False
        self.statuswidgits = []
        self.statusworkers = []
        self.statushandler = []
        self.users = []
        self.commands = []
        self.commandlock = threading.Lock()
        self.commandhandler = None
        self.connectionqueue = Queue.CircularQueue(10)
        self.update = False
        self.shutdown = False
        self.printlock = threading.Lock()
    def AddUser(self, type, connection):
        if type == "<CLIENT>":
            print("NEW CLIENT CONNECTED")
            self.connectionqueue.EnQueue(connection)
        elif type == "<STATUS_WORKER>":
            print("NEW STATUS WORKER CONNECTED")
            if not any(statuswidgit.name == connection.name for statuswidgit in self.statuswidgits):
                newstatuswidgit = StatusWidgit(self.widgit, connection)
                self.statuswidgits.append(newstatuswidgit)
                self.statusworkers.append(Workers.StatusWorkerServer(connection))
            else:
                for worker in self.statusworkers:
                    if worker.name == connection.name:
                        worker.connection = connection
            self.statusupdate = True
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
                        data = conn.recv(1024).decode()
                        print(data)
                    if data[0:11] == "<CONNECTED>":
                        objconn = Connection.Connection(conn, addr, data[11:])
                        objconn.Send(b"<WELCOME " + objconn.name.encode('utf-8') + b">")
                        data = conn.recv(1024).decode()
                        self.AddUser(data, objconn)
                    else:
                        conn.sendall(b"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, THUS CONNECTION WILL BE TERMINATED")
                        conn.close()  
                        print(f"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, INSTEAD GOT {data[0:11]}")
            except KeyboardInterrupt:
                s.close()
    @Threading.threaded
    def RecieveCommand(self, connection):
        if connection.Recieve(1024).decode("utf-8", "ignore") != "<DONE_JOB>":
            raise Exception("RECEIVED INCORRECT RESPONSE")
        connection.Send(b"<GET_OUTPUT>")
        output = connection.Recieve(1024).decode("utf-8", "ignore")
        with self.printlock:
            while output != "<OUTPUT_DONE>":
                print(output, flush="")
                connection.Send(b"<NEXT_OUTPUT>")
                output = connection.Recieve(1024)
                output = output.decode("utf-8", "ignore")
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
                    for command in commands:
                        connection.Send(command.encode("utf-8"))
                        if connection.Recieve(1024).decode("utf-8", "ignore") != "<COMMAND_RECIEVED>":
                            raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send(b"<END>")
                    msg = connection.Recieve(1024).decode("utf-8", "ignore") 
                    if msg != "<END_RECIEVED>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send(b"<START_JOB>")
                    if shouldberestored:
                        self.RecieveCommand(connection)
                except KeyboardInterrupt:
                    connection.Send(b"<STOP_JOB>")
                    if connection.Recieve() != "<JOB_STOPPED>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send(b"<QUIT_JOB>")
                    if connection.Recieve() != "<JOB_QUIT>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    break
            else:
                time.sleep(0.2)
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
                    currentwidgit = None
                    for statuswidgit in self.statuswidgits:
                        if statuswidgit.name == worker.name:
                            currentwidgit = statuswidgit
                            break
                    ping, uploadspeed, online, isbusy = worker.StatusRequest()
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
        currentwidgit.uploadspeedwidgit.config(text=f"Upload Speed: " + ("%.2g" % uploadspeed) + "MBs")
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