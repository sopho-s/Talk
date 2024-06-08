import tkinter as tk
import os
from ..NetObject import Server

cServer = None

def SubmitCommands(commands, server):
    temp = commands.get("1.0","end").split("\n")
    commands = []
    for value in temp:
        if value != "":
            commands.append(value)
    with server.commandlock:
        server.commands.append(commands)
        print("COMMAND SUBMITTED")

def Update(server):
    server.update = True

def ShutdownServer(server, serverthread):
    print("SHUTTING DOWN")
    os._exit(1)

def StartServer(root, button):
    global cServer
    cServer = Server.Server("10.101.1.59", 4245, root)
    serverthread = None
    try:
        serverthread = cServer.StartServer()
    except:
        pass
    commands = tk.Text(root, height = 5, width = 52)
    update = tk.Button(root, width=20, height=2, text='Update', command=lambda: Update(cServer))
    submit = tk.Button(root, width=20, height=2, text='Submit', command=lambda: SubmitCommands(commands, cServer))
    shutdown = tk.Button(root, width=20, height=2, text='Shutdown', command=lambda: ShutdownServer(cServer, serverthread))
    button.pack_forget()
    commands.pack()
    update.pack()
    submit.pack()
    shutdown.pack()
    
def main():
    root = tk.Tk()
    button = tk.Button(root, text='Start Server', width=40, height=4, command=lambda: StartServer(root, button))
    button.pack_forget()
    button.pack()
    root.mainloop()