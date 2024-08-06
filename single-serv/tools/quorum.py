import json

from .command import cmd_add_quorum_dids, cmd_setup_quorum_dids
from .utils import get_base_ports

def create_quorum_config(did_config, clusters, cluster_start_idx, n_quorum_nodes):
    base_serv, base_grpc = get_base_ports()
    
    quorumlistconfig = []
    for q in range(n_quorum_nodes):
        serv = base_serv + q
        grpc = base_grpc + q

        qlistconf = {
            "type": 2,
            "address": did_config[q][0]
        }
        quorumlistconfig.append(qlistconf)
        cmd_setup_quorum_dids(did_config[q][0], serv, grpc)
    
    quorum_file_name = "quorumlist.json"

    with open("linux/" + quorum_file_name, "w") as f:
        json.dump(quorumlistconfig, f)

    # Create groupwise quorumlist
    for c in range(0, clusters):
        serv = base_serv + cluster_start_idx + c
        grpc = base_grpc + cluster_start_idx + c
        
        cmd_add_quorum_dids(serv, grpc, quorum_file_name)
