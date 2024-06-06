import Talk.NetObject.Client
import random

with open("clientnames.csv", "r") as f:
    names = f.read().split(",")
name = random.choice(names)
Client = Talk.NetObject.Client.CommandClient(name.encode("utf-8"))
Client.ConnectClient("10.101.1.59", 4245)