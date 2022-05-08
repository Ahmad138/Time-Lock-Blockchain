#!/usr/bin/env python

import os
import datetime
import time
import hashlib
import base64
from cryptography.fernet import Fernet
#from Crypto import Random

class Timelock:
    def __init__(self) -> None:
        pass

    def generate_by_time(self, seed, delta):
        end = time.time() + delta.total_seconds()
        h = hashlib.sha256(str(seed).encode('utf-8')).digest()
        iters = 0
        try:
            while time.time() < end:
                h = hashlib.sha256(h).digest()

                iters += 1
        except:
            print("exception after %r iters", iters)
            print("time until end:", end - time.time())
            print("key is", base64.urlsafe_b64encode(h))
            raise

        return base64.urlsafe_b64encode(h), iters


    def generate_by_iters(self, seed, iters):
        h = hashlib.sha256(str(seed).encode('utf-8')).digest()
        for x in range(iters):
            h = hashlib.sha256(h).digest()
        return base64.urlsafe_b64encode(h)

    def generate_seed(self, x):    
        #x ==> number of timeblocks
        IV = []       
        seed = []
        for i in range(x):
            s = str(os.urandom(64))
            y = hashlib.sha256(str(s).encode('utf-8')).digest()

            IV.append(s)
            seed.append(y)

        return seed

    def timeblock(self, seed, d):    
        h, n = self.generate_by_time(str(seed), d) 

        return h, n

    def chain(self, seed, h):
        timechain = []
        for num, i in enumerate(seed):
            #print(num)
            if num < len(seed)-1:
                #print(seed[num+1])
                timechain.append(Fernet(h[num]).encrypt(seed[num+1]))
        return timechain

    def lock(self, key, message):
        #key ==> h[-1]
        return Fernet(key).encrypt(str(message).encode('utf-8'))

    def unlock(self, n, seed, timechain, timelocked_msg):
        #seed ==> is the first seed only that's needed
        h = self.generate_by_iters(str(seed), n[0])
        
        for num, i in enumerate(timechain):        
            if Fernet(h).decrypt(i):
                seed = Fernet(h).decrypt(i)
                if num < len(timechain):
                    h = self.generate_by_iters(str(seed), n[num+1])
        return Fernet(h).decrypt(timelocked_msg)

