import binascii
import os

def download_rubix_binary(dest):
    pass

def download_ipfs(dest):
    pass

def generate_swarm_key(dest):
    try:
        key = os.urandom(32)
    except Exception as e:
        print("While trying to read random source:", e)
        return

    output = "/key/swarm/psk/1.0.0/\n/base16/\n" + binascii.hexlify(key).decode()

    filename = f"{dest}/testswarm.key"

    if not os.path.exists(dest):
        os.makedirs(dest)

    with open(filename, "w") as file:
        file.write(output)

def per_group():

    pass


def per_system():
    # download prerequisite

    pass