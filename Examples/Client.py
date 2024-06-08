import Talk.NetObject.Client
import random
import os.path
import json
from pathlib import Path


with open("clientnames.csv", "r") as f:
    names = f.read().split(",")
commands = ""
with open("Commands.json", "r") as f:
    commands = json.loads(f.read())
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
Client = Talk.NetObject.Client.CommandClient(name.encode("utf-8"), commands)
Client.ConnectClient("10.101.1.59", 4245)