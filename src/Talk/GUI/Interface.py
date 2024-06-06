import tkinter as tk
from ..NetObject import Server

cServer = None

def SubmitCommands(commands, isupdate, server):
    commands = commands.get("1.0","end").split("\n")
    if isupdate:
        commands.append("<UPDATE>")
    commands.append("<END>")
    with server.commandlock:
        server.commands.append(commands)
        print("COMMAND SUBMITTED")
    

def StartServer(root):
    global cServer
    cServer = Server.MultiConnSingleInstructionServerWithCommands("10.101.1.59", 4245)
    try:
        serverthread = cServer.StartServer()
    except:
        pass
    ServerInfo = tk.Tk()
    commands = tk.Text(ServerInfo, height = 5, width = 52)
    update = tk.Button(ServerInfo, width=20, height=2, text='Submit and update', command=lambda: SubmitCommands(commands, True, cServer))
    submit = tk.Button(ServerInfo, width=20, height=2, text='Submit', command=lambda: SubmitCommands(commands, False, cServer))
    commands.pack()
    update.pack()
    submit.pack()
    root.destroy()
    ServerInfo.mainloop()

def main():
    root = tk.Tk()
    button = tk.Button(root, text='Start Server', width=40, height=4, command=lambda: StartServer(root))
    button.pack()
    root.mainloop()