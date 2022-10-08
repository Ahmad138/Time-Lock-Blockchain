import os
import sys
import datetime
import time
import socket  
import random
import math
#sys.path.insert(1, os.getcwd())

# Load .env file using:
from dotenv import load_dotenv

sys.path.insert(0, '..')  # Import the files where the modules are located

from wallet.keys import Keys as k
from blockchain.timelock import Timelock as timelock
from app.p2p_network.p2pnetwork.node import Node


load_dotenv()

"""

Note: If you get this error;

Traceback (most recent call last):
  ...  
  ...
    from p2pnetwork.nodeconnection import NodeConnection
ModuleNotFoundError: No module named 'p2pnetwork'

change:
from p2pnetwork.nodeconnection import NodeConnection
to
from .nodeconnection import NodeConnection

in node.py file

"""

class Tests():
    def __init__(self):
        #start main_node here
        self.node_1 = Node(str(os.getenv("IP")), int(os.getenv("PORT")), callback=self.node_callback) 
        time.sleep(1)
        self.node_1.start()
        time.sleep(1)
        self.TL = timelock()

    def test_keys(self):
        pr = k.gen_keys()
        f1 = 'pr_key.pem'
        k.save_key(pr, f1)
        _pr = k.load_key(f1)
        _pu = _pr.public_key()
        print(_pr)
        print(_pu)

    def test_timelock(self):
        """
        Requirments from stored system:
        1. pr/pu keys
        2. SECONDS_PER_SEED
        3. REDUNDANCIES

        Requirments from user:
        1. digital asset
        2. total timedelta

        """
        #Use saved keys
        f1 = 'pr_key.pem'
        _pr = k.load_key(f1)
        _pu = _pr.public_key()

        #test timelock
        msg = b"This is a secret"
        signature = k.sign(msg, _pr)
        #print(signature)
        d = datetime.timedelta(seconds=5)
        d = d.total_seconds()

        #test_timelock_1()
        TL = timelock()
        number_of_seeds = math.ceil(d/float(os.getenv("SECONDS_PER_SEED")))
        #print(number_of_seeds)
        seeds = TL.generate_seed(number_of_seeds)

        # After this point, choose the lucky winners and send to different nodes
        nodes = [['127.0.0.1', 8011], ['127.0.0.1', 8002], ['127.0.0.1', 8003], ['127.0.0.1', 8004], ['127.0.0.1', 8005], ['127.0.0.1', 8006], ['127.0.0.1', 8007], ['127.0.0.1', 8008], ['127.0.0.1', 8009], ['127.0.0.1', 8010]]
        paired_node_winners = TL.lot(nodes, number_of_seeds, float(os.getenv("REDUNDANCIES")), seeds)

        #print(paired_node_winners)
        shuffled_paired_node_winners = TL.custom_shuffle(paired_node_winners)             
        #print(shuffled_paired_node_winners)

        # loop(connect, send data, disconnect)
        for i in shuffled_paired_node_winners:
            
            msg = {
                "id": random.randint(1,999999999999),
                "operation": "timeblock",
                "seed": i[1],
                "delta": float(os.getenv("SECONDS_PER_SEED")),
                "return_node_id": self.node_1.id
            }

            self.p2p_comm(i[0], msg)

        #self.node_1.stop()
        # All the nodes, including the redundancies will perform this task each and return h, n, their pu for rewards etc
        
        """
        
       
        h, n = TL.timeblock(seed, d)

        
        #Perform math for standard deviation, mean etc and select again, at random, from the top 10 (size to be determined) of each set of similar seed nodes.
        # From that list, randomly select a single winner per seed to proceed with the chaining
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
        """

    def test_p2p(self):
        # Just for test we spin off multiple nodes, however it is more likely that these nodes are running
        # on computers on the Internet! Otherwise we do not have any peer2peer application.
        node_1 = Node("127.0.0.1", 8002, callback=self.node_callback)
        node_2 = Node("127.0.0.1", 8003, callback=self.node_callback)
        node_3 = Node("127.0.0.1", 8004, callback=self.node_callback)

        time.sleep(1)
        # node_1.debug = True
        # node_2.debug = True
        # node_3.debug = True
        node_1.start()
        node_2.start()
        node_3.start()
        time.sleep(1)

        node_1.connect_with_node('127.0.0.1', 8003)
        node_2.connect_with_node('127.0.0.1', 8004)
        node_3.connect_with_node('127.0.0.1', 8002)

        time.sleep(2)

        node_1.send_to_nodes("message: hi from node 2")

        #time.sleep(5)

        node_1.stop()
        node_2.stop()
        node_3.stop()

        print('end')

    def node_callback(self, event, main_node, connected_node, data):
        """The big callback method that gets all the events that happen inside the p2p network.

        Implement here your own application logic. The event holds the event that occurred within
        the network. The main_node contains the node that is handling the connection with and from
        other nodes. An event is most probably triggered by the connected_node! If there is data
        it is represented by the data variable. """
        
        try:
        # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            if event != 'node_request_to_stop':
                #print('Event: {} from main node {}: connected node {}: {}'.format(event, main_node.id, connected_node.id, data))
                key = ["id",  "operation", "seed", "delta", "return_node_id"]           
                if data.get(key[1]) is not None:
                    if data.get(key[1]) == "timeblock":
                        h, n = self.TL.timeblock(data.get(key[2]), data.get(key[3]))
                        #print(n)
                        msg = {
                                "id": random.randint(1,999999999999),
                                "operation": "timeblocked",
                                "h": (h).decode('utf-8'),
                                "n": n,
                                "return_node_id": main_node.id
                            }
                        
                        for node in main_node.nodes_inbound:                        
                            if data.get(key[4]) == node.id:
                                main_node.send_to_node(node, msg)
                                #print(node)                        
                else:
                    print(f"key: '{key[0]}' does not exists in dictionary")
            
        except Exception as e:
            print(e)
         
               
    def get_ip(self): 
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname)   
        print("Your Computer Name is:"+hostname)   
        print("Your Computer IP Address is:"+IPAddr)
        #return True 
    
    def test_dotenv(self):
        print(os.getenv("PYTHON_ENV"))

    def test_gen_seed_and_broadcast(self):
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
        seed = TL.generate_seed(2)

        nodes = [['127.0.0.1', 8001], ['127.0.0.1', 8002], ['127.0.0.1', 8003], ['127.0.0.1', 8004], ['127.0.0.1', 8005]]

        used_nodes=[]
        redundancies = 1
        node_seed_pairs = []

        if len(nodes) > len(seed):            
            for i in seed:
                for j in range(redundancies):
                    x = random.choice(tuple(nodes))
                    while x in used_nodes:
                        x = random.choice(tuple(nodes))
                    used_nodes.append(x)
                    temp = []
                    temp.append(x)
                    temp.append(i)

                    node_seed_pairs.append(temp)
                    print("node: {} and seed: {}".format(x, i))
        else:
            print("You need more nodes in the network")
        
        #print(node_seed_pairs)

    def p2p_comm(self, node, msg):
        # Just for test we spin off multiple nodes, however it is more likely that these nodes are running
        # on computers on the Internet! Otherwise we do not have any peer2peer application.
        #print("node: {} and msg: {}".format(node, msg))
        
        self.node_1.connect_with_node(node[0], node[1])

        time.sleep(1)               
        if len(self.node_1.nodes_outbound) > 0 : 
            self.node_1.send_to_node(self.node_1.nodes_outbound[-1], msg)
        time.sleep(1)
        
        #node_1.disconnect_with_node(node[1])

    def mass_p2p_comm(self, nodes, msg):
        # Just for test we spin off multiple nodes, however it is more likely that these nodes are running
        # on computers on the Internet! Otherwise we do not have any peer2peer application.
        node_1 = Node(str(os.getenv("IP")), int(os.getenv("PORT")), callback=self.node_callback)

        time.sleep(1)
        node_1.start()
        time.sleep(1)

        for num, node in enumerate(nodes):
            node_1.connect_with_node(node[0], node[1])

        time.sleep(2)
        node_1.send_to_nodes(msg)
        time.sleep(1)

        node_1.stop()
    
    def test_p2p(self):
        seed = 'b"GFv\\xd6\\x1a\\x1e%\'\\xdf\\xf6\\xe7\\x07=\\xb1\\xceG\\xf5JR\\xc5\\xf2\\xf5\\xa7\\xc5\\x04 \\x06i\\x05X\\xbd\\x8d\\x87\\xf9\\xe1\\r`\\xd8g\\xd6\\xe7W\\xe9<2\\x85\\xa7\\xf3\\xeb\\x82\\x82A\\xdd\\x00\\x85\\xbf\\x8b\\xcf\\xbfz}\\xc2Xj"'
        msg = {
            "id": random.randint(1,999999999999),
            "operation": "timeblock",
            "seed": seed,
            "delta": float(os.getenv("SECONDS_PER_SEED")),
            "return_node_id": self.node_1.id
        }
        self.p2p_comm(['127.0.0.1', 8002], msg)