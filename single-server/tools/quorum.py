import json

from .command import cmd_add_quorum_dids, cmd_setup_quorum_dids
from .utils import get_base_ports

def create_quorum_config(did_config, clusters, n_quorum_nodes):
    base_serv, base_grpc = get_base_ports()
    
    # Create groupwise quorumlist

    for c in range(0, clusters):
        serv = base_serv + c
        grpc = base_grpc + c

        quorumlistconfig = []
        quorum_file_name = "quorumlist_" + str(c + 1) + ".json"
        print(f"iter {c} , {quorum_file_name}")
        
        for q in range(n_quorum_nodes):
            qlistconf = {
                "type": 2,
                "address": did_config[c][q]
            }
            quorumlistconfig.append(qlistconf)
            cmd_setup_quorum_dids(did_config[c][q], serv, grpc)

        with open("linux/" + quorum_file_name, "w") as f:
            json.dump(quorumlistconfig, f)

        cmd_add_quorum_dids(serv, grpc, quorum_file_name)
