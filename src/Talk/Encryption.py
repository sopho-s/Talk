import time
import random
import math
import time
from scipy import special
 
 
class Key:
    def __init__(self, public, private):
        self.public = public
        self.private = private
 
 
def listsize(nth):
    tempnum = math.e ** (-special.lambertw(-1/nth, k=1))
    return int(tempnum)

def getprimes(nth):
    if nth != 1:
        size = listsize(nth)
        posprimes = [0 for i in range(0, size)]
        posprimes[0] = 1
        primes = [2]
        count = 3
        while len(primes) < nth:
            if posprimes[count] == 0:
                primes.append(count)
                mult = 0
                while mult*count < size:
                    posprimes[mult*count] = 1
                    mult += 1
            count += 2
        return primes
    return [2]

def getnthprime(nth):
    primes = getprimes(nth)
    return primes[nth-1]

def Getpartrand():
    start = time.time()
    time.sleep(0.01)
    key = time.time() - start
    start = time.time()
    time.sleep(0.01)
    key = key * 10 ** ((time.time() - start - 0.01) * 1000)
    key = int(key * 2 ** 128) % 2 ** 128
    return key

def GenerateRandom():
    stringkey = ""
    for _ in range(20):
        stringkey += str(Getpartrand())
    keylen = len(stringkey)
    output = 0
    count = 0.7723
    for char in stringkey:
        output += (int(char) ** count) % (2**64)
        count += 0.7723
        if count > 128:
            count -= 128
    return int(output * keylen) % (10**12)

def GenPrimes():
    prime1 = 0
    while prime1 < 500:
        prime1 = getnthprime(GenerateRandom() % (10 ** 5))
    prime2 = 0
    while prime2 < 500:
        prime2 = getnthprime(GenerateRandom() % (10 ** 5))
    return prime1, prime2

def RSA():
    prime1, prime2 = GenPrimes()
    n = prime1 * prime2
    phi = (prime1-1) * (prime2-1)
    e = 2
    while phi % e == 0:
        e += 1
    d = pow(e, -1, phi)
    return e, d, n

def EncryptRSA(data, e, n):
    return pow(data, e, n)

def DecryptRSA(data, d, n):
    return pow(data, d, n)