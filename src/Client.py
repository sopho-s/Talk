import Talk.NetObject.Client


HelloClient = Talk.NetObject.Client.SleepyClient(1)
HelloClient.ConnectClient("10.0.0.140", 42424)