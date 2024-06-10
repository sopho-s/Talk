import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.NetObject import Server as S

Server = S.Server("10.101.1.59", 42425)
serverthread = Server.StartServer()