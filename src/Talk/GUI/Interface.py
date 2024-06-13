try:
    import Tkinter as tk
except ModuleNotFoundError:
    import tkinter as tk
    
import os, json, random
from pathlib import Path
from ..NetObject import Server, Client

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

def StartServer(root, button, cServer):
    serverthread = cServer.StartServer()
    commands = tk.Text(root, height = 5, width = 52)
    update = tk.Button(root, width=20, height=2, text='Update', command=lambda: Update(cServer))
    submit = tk.Button(root, width=20, height=2, text='Submit', command=lambda: SubmitCommands(commands, cServer))
    shutdown = tk.Button(root, width=20, height=2, text='Shutdown', command=lambda: ShutdownServer(cServer, serverthread))
    button.pack_forget()
    commands.pack()
    update.pack()
    submit.pack()
    shutdown.pack()
    
def Apply(accept, cServer):
    if accept.get():
        cServer.acceptall = True
    else:
        cServer.acceptall = False
        
    
    
def MakeSettings(root, cServer):
    settings = tk.Toplevel(root)
    settings.geometry("200x200")
    accept = None
    acceptvar = tk.BooleanVar()
    acceptText = tk.Label(settings, text='Accept All')
    accept = tk.Checkbutton(settings, variable=acceptvar)
    apply = tk.Button(settings, text="Apply", command=lambda: Apply(acceptvar, cServer))
    acceptText.grid_columnconfigure(0, weight=1)
    accept.grid_columnconfigure(1, weight=1)
    apply.grid_columnconfigure(0, weight=1)
    acceptText.grid(row=0, column=0)
    accept.grid(row=0, column=1)
    apply.grid(row=1)
    
    
def ServerInterface(ip, port, commands):
    root = tk.Tk()
    cServer = Server.Server(ip, port, commands, root)
    button = tk.Button(root, text='Start Server', width=40, height=4, command=lambda: StartServer(root, button, cServer))
    button.pack_forget()
    button.pack()
    MakeSettings(root, cServer)
    root.mainloop()

def ClientInterface(ip, port, commands):
    with open("clientnames.csv", "r") as f:
        names = f.read().split(",")
    name = ""
    key = 0
    if os.path.isfile(os.path.expanduser( '~' ) + "/clientid.key"):
        with open(os.path.expanduser( '~' ) + "/clientid.key", "r") as f:
            key = int(f.read())
            name = names[key % len(names)]
    else:
        key = random.randint(0, 2**64)
        Path(os.path.expanduser( '~' ) + "/clientid.key").touch()
        with open(os.path.expanduser( '~' ) + "/clientid.key", "w") as f:
            f.write(str(key))
        name = names[key % len(names)]
    client = Client.RequestClient(name.encode("utf-8"), commands, key)
    client.ConnectClient(ip, port)
    root = tk.Tk()
    commands = tk.Text(root, height = 5, width = 52)
    submit = tk.Button(root, width=20, height=2, text='Submit', command=lambda: SubmitClientCommands(commands, client))
    commands.pack()
    submit.pack()
    root.mainloop()

def SubmitClientCommands(commands, client):
    client.requests.EnQueue(commands)