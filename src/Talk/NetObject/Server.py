import socket
import time
import threading
import tkinter as tk
import os
from ..NetObject import Connection
from ..Threading import Threading
from ..Objects import Queue

class StatusWidgit:
    def __init__(self):
        self.widgit = None
        self.namewidgit = None
        self.name = None
        self.timetakenwidgit = None
        self.timetaken = None

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
    def StartServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            while True:
                s.listen()
                conn, addr = s.accept()
                objconn = Connection.Connection(conn, addr)
                with conn:
                    print(f"Connected by {addr}")
                    print(objconn.RecieveAll())
                        
class MultiConnServer(Server):
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
    def StartServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            while True:
                s.listen()
                conn, addr = s.accept()
                objconn = Connection.Connection(conn, addr)
                self.PrintData(objconn)
    @Threading.threaded
    def PrintData(self, connection):
        while True:
            print(f"Connected by {connection.address}")
            data = connection.Recieve(1024)
            if len(data) == 0:
                break
            else:
                print(data)

class SleepyMultiConnServer(MultiConnServer):
    def __init__(self, HOST, PORT, sleeptime):
        super().__init__(HOST, PORT)
        self.sleeptime = sleeptime
    @Threading.threaded
    def PrintData(self, connection):
        while True:
            print(f"Connected by {connection.address}")
            data = connection.Recieve(1024)
            if len(data) == 0:
                break
            else:
                print(data)
            time.sleep(self.sleeptime)

class MultiConnSingleInstructionServerWithCommands(MultiConnServer):
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
        self.commands = []
        self.commandlock = threading.Lock()
        self.commandhandler = None
        self.connectionqueue = Queue.CircularQueue(10)
        self.shutdown = False
    @Threading.threaded
    def StartServer(self):
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
                    if data[0:11] == "<CONNECTED>":
                        objconn = Connection.Connection(conn, addr, data[11:])
                        objconn.Send(b"<WELCOME " + objconn.name.encode('utf-8') + b">")
                        print("NEW CLIENT CONNECTED")
                        self.connectionqueue.EnQueue(objconn)
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
                    
class MultiConnSingleInstructionServerWithCommandsWidgitHandling(MultiConnSingleInstructionServerWithCommands):
    def __init__(self, HOST, PORT, widgit):
        super().__init__(HOST, PORT)
        self.widgit = widgit
        self.statusupdate = False
        self.statuswidgits = []
    @Threading.threaded
    def StartServer(self):
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
                    if data[0:11] == "<CONNECTED>":
                        objconn = Connection.Connection(conn, addr, data[11:])
                        objconn.Send(b"<WELCOME " + objconn.name.encode('utf-8') + b">")
                        print("NEW CLIENT CONNECTED")
                        self.connectionqueue.EnQueue(objconn)
                        newstatuswidgit = StatusWidgit()
                        clientwigit = tk.Toplevel(self.widgit)
                        clientwigit.geometry("200x100")
                        newstatuswidgit.name = objconn.name
                        newstatuswidgit.widgit = clientwigit
                        self.statuswidgits.append(newstatuswidgit)
                        name = tk.Label(clientwigit, text=objconn.name)
                        timetaken = tk.Label(clientwigit, text="")
                        clientwigit.grid_columnconfigure(0, weight=1)
                        name.grid_columnconfigure(0, weight=1)
                        name.grid(row=0)
                        timetaken.grid(row=1)
                        timetaken.grid_columnconfigure(1, weight=1)
                        newstatuswidgit.namewidgit = name
                        newstatuswidgit.timetakenwidget = timetaken
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
            elif self.statusupdate:
                for client in self.connectionqueue:
                    client.Send(b"<GIVE_STATUS>")
                    client.SetTimeout(10)
                    if client.Recieve(1024).decode() != "<OK_START>":
                        raise Exception("RECEIVED INCORRECT RESPONSE")
                    total = 0
                    for i in range(10):
                        client.Send(b"<PING>")
                        start = time.time()
                        if client.Recieve(1024).decode() != "<PONG>":
                            raise Exception("RECEIVED INCORRECT RESPONSE")
                        total += (time.time() - start) / 10
                    total *= 1000
                    for statuswidgit in self.statuswidgits:
                        if statuswidgit.name == client.name:
                            statuswidgit.timetaken = total
                            statuswidgit.timetakenwidget.config(text=f"Ping: " + ("%.0f" % total) + "ms")
                            if total < 10:
                                statuswidgit.timetakenwidget.config(fg="#00d100")
                            elif total < 40:
                                statuswidgit.timetakenwidget.config(fg="#99d100")
                            elif total < 100:
                                statuswidgit.timetakenwidget.config(fg="#e89f00")
                            elif total < 1000:
                                statuswidgit.timetakenwidget.config(fg="#ff2f00")
                            else:
                                statuswidgit.timetakenwidget.config(fg="#9e0000")
                    start = time.time()
                    client.SendFile(os.path.dirname(os.path.abspath(__file__)) + "\\Payload.csv")
                    print("Done")
                    client.SetTimeout(None)
                self.statusupdate = 0
            else:
                time.sleep(0.2)
                    