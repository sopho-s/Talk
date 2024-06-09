import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.GUI import Interface as talkint
from src.Talk import Encryption


'''e, d, n = Encryption.RSA()


num = int(input("ENTER NUMBERRRR"))

encrypted = Encryption.EncryptRSA(num, e, n)

print(encrypted)

decrypted = Encryption.DecryptRSA(encrypted, d, n)

print(decrypted)'''

talkint.main()