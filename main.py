from tests.test import Tests

def main():
    T = Tests()
    T.test_keys()
    T.test_timelock()
    T.get_ip()
    T.test_p2p()


if __name__ == "__main__":
    main()