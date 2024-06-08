import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))
from src.Talk.GUI import Interface as talkint

talkint.main()