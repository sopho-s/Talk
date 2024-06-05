import Talk.NetObject.Server

HelloServer = Talk.NetObject.Server.MultiConnServer("10.101.1.59", 42424)
HelloServer.StartServer()