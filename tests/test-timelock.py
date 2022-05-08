import os
import sys
import datetime
#import time
sys.path.insert(1, os.getcwd())

from wallet.keys import Keys as k
from blockchain.timelock import Timelock as timelock

def main():
    #Use saved keys
    f1 = 'pr_key.pem'
    _pr = k.load_key(f1)
    _pu = _pr.public_key()

    #test timelock
    msg = b"This is a secret"
    signature = k.sign(msg, _pr)
    #print(signature)
    d = datetime.timedelta(seconds=1)
    #test_timelock_1()
    TL = timelock()
    seed = TL.generate_seed(1)
    h, n = TL.timeblock(seed, d)

    e = TL.chain(seed, h)
    timelocked_msg = TL.lock(h, signature)

    #print(timelocked_msg)
    x=[]
    x.append(n)    
    unlocked = TL.unlock(x, seed, e, timelocked_msg)

    #print (unlocked)

    correct = k.verify(msg, signature, _pu)

    if correct:
        print("Success! Good signature")
    else:
        print("Error!!! Bad Signature")


if __name__ == "__main__":
    main()