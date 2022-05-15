import os
import sys
import datetime
import time
import socket  
#sys.path.insert(1, os.getcwd())

sys.path.insert(0, '..')  # Import the files where the modules are located

from wallet.keys import Keys as k
from blockchain.timelock import Timelock as timelock
from app.p2p_network.p2pnetwork.node import Node

class Tests():
    def __init__(self) -> None:
        pass

    def test_keys(self):
        pr = k.gen_keys()
        f1 = 'pr_key.pem'
        k.save_key(pr, f1)
        _pr = k.load_key(f1)
        _pu = _pr.public_key()
        print(_pr)
        print(_pu)

    def test_timelock(self):
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

    def test_p2p(self):
        # Just for test we spin off multiple nodes, however it is more likely that these nodes are running
        # on computers on the Internet! Otherwise we do not have any peer2peer application.
        node_1 = Node("127.0.0.1", 8001, callback=self.node_callback)
        node_2 = Node("127.0.0.1", 8002, callback=self.node_callback)
        node_3 = Node("127.0.0.1", 8003, callback=self.node_callback)

        time.sleep(1)
        # node_1.debug = True
        # node_2.debug = True
        # node_3.debug = True
        node_1.start()
        node_2.start()
        node_3.start()
        time.sleep(1)

        node_1.connect_with_node('127.0.0.1', 8002)
        node_2.connect_with_node('127.0.0.1', 8003)
        node_3.connect_with_node('127.0.0.1', 8001)

        time.sleep(2)

        node_1.send_to_nodes("message: hoi from node 1")

        time.sleep(5)

        node_1.stop()
        node_2.stop()
        node_3.stop()

        print('end')

    def node_callback(self, event, main_node, connected_node, data):
        """The big callback method that gets all the events that happen inside the p2p network.

        Implement here your own application logic. The event holds the event that occurred within
        the network. The main_node contains the node that is handling the connection with and from
        other nodes. An event is most probably triggered by the connected_node! If there is data
        it is represented by the data variable."""
        try:
            # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            if event != 'node_request_to_stop':
                print('Event: {} from main node {}: connected node {}: {}'.format(event, main_node.id, connected_node.id,
                                                                                data))

        except Exception as e:
            print(e)

    def get_ip(self): 
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname)   
        print("Your Computer Name is:"+hostname)   
        print("Your Computer IP Address is:"+IPAddr) 