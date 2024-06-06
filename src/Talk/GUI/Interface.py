import tkinter as tk
from ..NetObject import Server

cServer = None

def SubmitCommands(commands, isupdate, server):
    temp = commands.get("1.0","end").split("\n")
    commands = []
    for value in temp:
        if value != "":
            commmands.append(value)
    if isupdate:
        commands.append("<UPDATE>")
    with server.commandlock:
        server.commands.append(commands)
        print("COMMAND SUBMITTED")

def ShutdownServer(server):
    server.shutdown = True
    

def StartServer(root, button):
    global cServer
    cServer = Server.MultiConnSingleInstructionServerWithCommands("10.101.1.59", 4245)
    try:
        serverthread = cServer.StartServer()
    except:
        pass
    commands = tk.Text(root, height = 5, width = 52)
    update = tk.Button(root, width=20, height=2, text='Submit and update', command=lambda: SubmitCommands(commands, True, cServer))
    submit = tk.Button(root, width=20, height=2, text='Submit', command=lambda: SubmitCommands(commands, False, cServer))
    submit = tk.Button(root, width=20, height=2, text='Shutdown', command=lambda: ShutdownServer(cServer))
    button.pack_forget()
    commands.pack()
    update.pack()
    submit.pack()

def main():
    root = tk.Tk()
    button = tk.Button(root, text='Start Server', width=40, height=4, command=lambda: StartServer(root, button))
    button.pack_forget()
    button.pack()
    root.mainloop()