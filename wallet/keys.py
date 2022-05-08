from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Keys:
    def __init__(self) -> None:
        pass
    #Generate keys. Note: the public can be generated from the private key anytime
    def gen_keys():
        private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048, backend=default_backend()
        )

        #public_key = private_key.public_key()
        return private_key

    #Save the generated private key locally to a pem file for usage later
    def save_key(pk, filename):
        pem = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(filename, 'wb') as pem_out:
            pem_out.write(pem)

    #Load a saved private key from a pem file for usage anytime
    def load_key(filename):
        with open(filename, 'rb') as pem_in:
            pemlines = pem_in.read()
        private_key = load_pem_private_key(pemlines, None, default_backend())
        return private_key

    #Sign a message
    def sign(message, private):
        signature = private.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
        )
        return signature

    #Verify
    def verify(message, sig, public):
        try:
            public.verify(
            sig,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
            )
            return True
        except:
            print("Something went wrong with key verification!!!")
            return False
