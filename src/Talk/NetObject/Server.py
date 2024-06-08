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
        self.widgit = tk.Toplevel(widgit)
        self.widgit.geometry("200x100")
        self.name = objconn.name
        self.namewidgit = tk.Label(self.widgit, text=objconn.name)
        self.pingwidgit = tk.Label(self.widgit, text="")
        self.uploadspeedwidgit = tk.Label(self.widgit, text="")
        self.onlinewidgit = tk.Label(self.widgit, text="")
        self.widgit.grid_columnconfigure(0, weight=1)
        self.namewidgit.grid_columnconfigure(0, weight=1)
        self.pingwidgit.grid_columnconfigure(1, weight=1)
        self.uploadspeedwidgit.grid_columnconfigure(2, weight=1)
        self.onlinewidgit.grid_columnconfigure(3, weight=1)
        self.namewidgit.grid(row=0)
        self.pingwidgit.grid(row=1)
        self.uploadspeedwidgit.grid(row=2)
        self.onlinewidgit.grid(row=3)
class Server:
    def __init__(self, HOST, PORT, widgit):
        self.HOST = HOST
        self.PORT = PORT
        self.widgit = widgit
        self.statusupdate = False
        self.statuswidgits = []
        self.statusworkers = []
        self.statushandler = []
        self.commands = []
        self.commandlock = threading.Lock()
        self.commandhandler = None
        self.connectionqueue = Queue.CircularQueue(10)
        self.update = False
        self.shutdown = False
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
                        if data == "<CLIENT>":
                            print("NEW CLIENT CONNECTED")
                            self.connectionqueue.EnQueue(objconn)
                        elif data == "<STATUS_WORKER>":
                            print("NEW STATUS WORKER CONNECTED")
                            if not any(statuswidgit.name == objconn.name for statuswidgit in self.statuswidgits):
                                self.statusworkers.append(Workers.StatusWorkerServer(objconn))
                                newstatuswidgit = StatusWidgit(self.widgit, objconn)
                                self.statuswidgits.append(newstatuswidgit)
                            else:
                                for worker in self.statusworkers:
                                    if worker.name == objconn.name:
                                        worker.connection = objconn
                            self.statusupdate = True
                    else:
                        conn.sendall(b"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, THUS CONNECTION WILL BE TERMINATED")
                        conn.close()  
                        print(f"CLIENT ATTEMPTED TO CONNECT TO A COMMAND SERVER WITHOUT COMMANDS, INSTEAD GOT {data[0:11]}")
            except KeyboardInterrupt:
                s.close()
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
                        if command == "<UPDATE>":
                            connection.Send(b"git pull")
                            if connection.Recieve(1024).decode() != "<COMMAND_RECIEVED>":
                                raise Exception("RECEIVED INCORRECT RESPONSE")
                            connection.Send(b"<RESET>")
                            if connection.Recieve(1024).decode() != "<COMMAND_RECIEVED>":
                                raise Exception("RECEIVED INCORRECT RESPONSE")
                            shouldberestored = False
                        else:
                            connection.Send(command.encode("utf-8"))
                            if connection.Recieve(1024).decode() != "<COMMAND_RECIEVED>":
                                raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send(b"<END>")
                    if connection.Recieve(1024).decode() != "<END_RECIEVED>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    connection.Send(b"<START_JOB>")
                    if shouldberestored:
                        if connection.Recieve(1024).decode() != "<DONE_JOB>":
                            raise Exception("RECEIVED INCORRECT RESPONSE")
                        connection.Send(b"<GET_OUTPUT>")
                        output = connection.Recieve(1024).decode()
                        count = 1
                        while output != "<OUTPUT_DONE>":
                            print(f"COMMAND {count}:")
                            count += 1
                            print(output)
                            print("\n\n")
                            connection.Send(b"<NEXT_OUTPUT>")
                            output = connection.Recieve(1024).decode()
                        connection = self.connectionqueue.EnQueue(connection)
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
            if self.statusupdate:
                print("REQUESTING STATUS")
                for worker in self.statusworkers:
                    currentwidgit = None
                    for statuswidgit in self.statuswidgits:
                        if statuswidgit.name == worker.name:
                            currentwidgit = statuswidgit
                            break
                    if not worker.connection.CheckOnline():
                        currentwidgit.pingwidgit.config(text=f"Ping: 0ms")
                        currentwidgit.uploadspeedwidgit.config(text=f"Upload Speed: 0MBs")
                        currentwidgit.onlinewidgit.config(text=f"Offline")
                        currentwidgit.onlinewidgit.config(fg="#9e0000")
                        continue
                    currentwidgit.onlinewidgit.config(text=f"Online")
                    currentwidgit.onlinewidgit.config(fg="#00d100")
                    ping, uploadspeed, online = worker.StatusRequest()
                    if not online:
                        currentwidgit.pingwidgit.config(text=f"Ping: 0ms")
                        currentwidgit.uploadspeedwidgit.config(text=f"Upload Speed: 0MBs")
                        currentwidgit.onlinewidgit.config(text=f"Offline")
                        currentwidgit.onlinewidgit.config(fg="#9e0000")
                        continue
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
                        statuswidgit.uploadspeedwidgit.config(fg="#ff2f00")
                    elif uploadspeed < 1:
                        currentwidgit.uploadspeedwidgit.config(fg="#e89f00")
                    elif uploadspeed < 5:
                        currentwidgit.uploadspeedwidgit.config(fg="#99d100")
                    else:
                        currentwidgit.uploadspeedwidgit.config(fg="#00d100")
                self.statusupdate = False
            else:
                time.sleep(0.5)
                self.statusupdate = True