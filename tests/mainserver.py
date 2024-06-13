import sys, os, json
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.GUI import Interface as talkint

commands = ""
with open("Commands.json", "r") as f:
    commands = json.loads(f.read())
talkint.ServerInterface("10.101.1.59", 42425, commands)