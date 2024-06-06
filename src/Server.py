import Talk.NetObject.Server

Server = Talk.NetObject.Server.MultiConnSingleInstructionServerWithCommands("10.101.1.59", 4245)
serverthread = Server.StartServer()

try:
    while True:
        command = ""
        commands = []
        while command != "<END>":
            command = input("ENTER COMMAND: ")
            commands.append(command)
        print("SUBMITTING COMMAND")
        with Server.commandlock:
            Server.commands.append(commands)
            print("COMMAND SUBMITTED")
except KeyboardInterrupt:
    Server.shutdown = True