import Talk.NetObject.Client
import random
import os.path
from pathlib import Path


with open("clientnames.csv", "r") as f:
    names = f.read().split(",")
name = ""
if os.path.isfile(os.path.expanduser( '~' ) + "/clientid.key"):
    with open(os.path.expanduser( '~' ) + "/clientid.key", "r") as f:
        name = names[int(f.read())]
else:
    key = random.randint(0, len(names))
    Path(os.path.expanduser( '~' ) + "/clientid.key").touch()
    with open(os.path.expanduser( '~' ) + "/clientid.key", "w") as f:
        f.write(str(key))
    name = names[key]
Client = Talk.NetObject.Client.CommandClient(name.encode("utf-8"))
Client.ConnectClient("10.101.1.59", 4245)