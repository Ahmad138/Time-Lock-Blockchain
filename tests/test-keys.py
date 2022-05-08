import os
import sys
sys.path.insert(1, os.getcwd())

from wallet.keys import Keys as k

def main():
    pr = k.gen_keys()
    f1 = 'pr_key.pem'
    k.save_key(pr, f1)
    _pr = k.load_key(f1)
    _pu = _pr.public_key()
    print(_pr)
    print(_pu)


if __name__ == "__main__":
    main()