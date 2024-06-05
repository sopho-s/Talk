import Talk.NetObject.Client


Client = Talk.NetObject.Client.CommandClient(b"ALICE")
Client.ConnectClient("10.101.1.59", 4245)