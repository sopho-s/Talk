import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.NetObject import Client as C
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
key = 0
if os.path.isfile(os.path.expanduser( '~' ) + "/clientid.key"):
    with open(os.path.expanduser( '~' ) + "/clientid.key", "r") as f:
        key = int(f.read())
        name = names[key]
else:
    key = random.randint(0, 2**64))
    Path(os.path.expanduser( '~' ) + "/clientid.key").touch()
    with open(os.path.expanduser( '~' ) + "/clientid.key", "w") as f:
        f.write(str(key))
    name = names[key % len(names)]
Client = C.CommandClient(name.encode("utf-8"), commands, key)
Client.ConnectClient("10.101.1.59", 4245)