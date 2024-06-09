import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.Talk.GUI import Interface as talkint
from src.Talk import Encryption
from src.Talk.Objects import Bits


'''e, d, n = Encryption.RSA()


num = int(input("ENTER NUMBERRRR"))

encrypted = Encryption.EncryptRSA(num, e, n)

print(encrypted)

decrypted = Encryption.DecryptRSA(encrypted, d, n)

print(decrypted)'''

key1, key2, key3, key4 = Encryption.EncryptionKeyGen()

print(Bits.BitArray(key1))
print(Bits.BitArray(key2))
print(Bits.BitArray(key3))
print(Bits.BitArray(key4))

data = Encryption.Encrypt("hello my name is nick and this is a fairly long sentance", key1, key2, key3, key4)

print(data)

print(Encryption.Decrypt(data, key1, key2, key3, key4))

#talkint.main()