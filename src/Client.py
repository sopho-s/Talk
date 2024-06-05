import Talk.NetObject.Client


HelloClient = Talk.NetObject.Client.SleepyClient(1)
HelloClient.ConnectClient("10.101.1.59", 42424)