import Talk.NetObject.Client
import random
import os


with open("clientnames.csv", "r") as f:
    names = f.read().split(",")
name = ""
key = os.environ.get("CLIENTID", False)
if key:
    name = names[key]
else:
    key = random.randint(0, len(names))
    os.environ["CLIENTID"] = key
    with open("clientid.key", "w") as f:
        f.write(str(key))
    name = names[key]
Client = Talk.NetObject.Client.CommandClient(name.encode("utf-8"))
Client.ConnectClient("10.101.1.59", 4245)