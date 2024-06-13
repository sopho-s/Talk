import sys, os, json
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.NetObject import Server as S

commands = ""
with open("Commands.json", "r") as f:
    commands = json.loads(f.read())
Server = S.Server("10.101.1.59", 42425, commands)
serverthread = Server.StartServer()