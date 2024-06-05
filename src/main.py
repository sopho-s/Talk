import Talk.NetObject.Server

HelloServer = Talk.NetObject.Server.MultiConnServer("10.0.0.140", 42424)
HelloServer.StartServer()