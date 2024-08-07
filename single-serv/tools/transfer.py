from .command import get_transfer_cmd_str, cmd_rbt_transfer
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from .utils import get_base_ports
import json


def intiate_transfer(did_list, n_cluster, cluster_start_idx, n_non_quorum_dids):
    # Make a list of transfer commands 
    commands = []
    base_serv, base_grpc = get_base_ports()

    request_list = []

    for c in range(0, n_cluster):
        k = cluster_start_idx + c
        serv = base_serv + k
        grpc = base_grpc + k

        for q in range(0, n_non_quorum_dids, 2):
            req = {
                "comment": "send",
                "receiver": did_list[k][q+1],
                "sender": did_list[k][q],
                "tokenCount": 1,
                "type": 2
            }
            request_list.append(req)

    save_reqs(request_list, "reqs.json")

def save_reqs(b, filename):
    with open(filename, 'w') as file:
        json.dump(b, file)