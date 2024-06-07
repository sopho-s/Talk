import Talk.NetObject.Client
import random
import os.path


with open("clientnames.csv", "r") as f:
    names = f.read().split(",")
name = ""
if os.path.isfile("~/clientid.key"):
    with open("~/clientid.key", "r") as f:
        name = names[int(f.read())]
else:
    key = random.randint(0, len(names))
    with open("~/clientid.key", "w") as f:
        f.write(str(key))
    name = names[key]
Client = Talk.NetObject.Client.CommandClient(name.encode("utf-8"))
Client.ConnectClient("10.101.1.59", 4245)