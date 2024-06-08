import Talk.NetObject.Server

Server = Talk.NetObject.Server.Server("10.101.1.59", 4245)
serverthread = Server.StartServer()