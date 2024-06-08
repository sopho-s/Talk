import time
import random

def GenerateRandom():
    start = time.time()
    time.sleep(0.01)
    key = time.time() - start
    start = time.time()
    time.sleep(0.01)
    key = key * 10 ** ((time.time() - start - 0.01) * 1000)
    key = int(key * 2 ** 128) % 2 ** 128
    return key

def GenerateKey():
    stringkey = ""
    for _ in range(20):
        stringkey += str(GenerateRandom())
    keylen = len(stringkey)
    output = 0
    count = 0.7723
    for char in stringkey:
        output += (int(char) ** count) % (2**64)
        count += 0.7723
        if count > 128:
            count -= 128
    return int(output * keylen) % (10**12)