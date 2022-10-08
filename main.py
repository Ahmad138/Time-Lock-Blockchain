from tests.test import Tests

#after random set of people have generated timeblocks, random set of people will verify each computation with extra redundencies in paralell before chaining
#Have a list of nodes and ports. Only p2p connect when that node is randomly selected and there is a job to send to save resources. if failed to connect, choose another random node


def main():
    T = Tests()    
    #T.get_ip()
    #T.test_keys()
    T.test_p2p()
    #T.test_timelock()
    #T.test_p2p()
    #T.test_dotenv()
    #T.test_gen_seed_and_broadcast()
    

if __name__ == "__main__":
    main()