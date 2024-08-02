import subprocess
import os
import time
import requests
import platform
import re
import json

def get_base_ports():
    base_ens_server = 20000
    base_grpc_port = 10500

    return base_ens_server, base_grpc_port

non_functional_nodes_port = []

for i in range(1, 51):
    base_server, _ = get_base_ports()
    port = base_server + i
    url = f"http://localhost:{port}/api/getalldid"

    try:
        print(f"Sending GET request to URL: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            non_functional_nodes_port.append(port)
    except:
        non_functional_nodes_port.append(port)

print(non_functional_nodes_port)