import sys

'''
Args:
    1 (int): to install prereq
'''

from tools.prerequisite import *
from tools.command import *
from tools.utils import get_base_ports, save_to_json, load_from_json
from tools.quorum import create_quorum_config
from tools.transfer import intiate_transfer

TARGET_TRANSACTIONS = 90

QUORUM_NODES_PER_CLUSTER = 7
NON_QUORUM_NODES_PER_CLUSTER = 2
NODES_PER_CLUSTER = QUORUM_NODES_PER_CLUSTER + NON_QUORUM_NODES_PER_CLUSTER

CLUSTERS = int(TARGET_TRANSACTIONS / NODES_PER_CLUSTER)

TOTAL_DID = TARGET_TRANSACTIONS * NODES_PER_CLUSTER
TOTAL_DID_PER_CLUSTER = int(TOTAL_DID / CLUSTERS)

if __name__=='__main__':
    rerun_flag = -1
    if len(sys.argv) >= 2:
        rerun_flag = int(sys.argv[1])
    
    # Installing prereque
    print("Installing prereq")

    download_rubix_binary()
    download_ipfs_binary("Linux", "v0.21.0", "linux")
    generate_ipfs_swarm_key()

    # start a server
    print("Starting Rubix Servers")

    for r in range(CLUSTERS):
        print("Starting Server " + str(r))
        node_idx = r
        base_serv, base_grpc = get_base_ports()
        
        serv, grpc = base_serv + node_idx, base_grpc + node_idx 
        node_name = "node" + str(r)
        
        cmd_run_rubix_servers(node_name, node_idx)

    input("Wait for about 80 seconds and hit Enter")
    
    # create did

    print(f"Creating {TOTAL_DID} DIDs")
    
    '''
    {
        0: [did1, did2],
        1: [did3, did4]
    }
    '''
    did_config_list = {}

    for c in range(CLUSTERS):
        serv = base_serv + c
        grpc = base_grpc + c
        did_config_list[c] = []

        for _ in range(TOTAL_DID_PER_CLUSTER):    
            d = cmd_create_did(serv, grpc)
            cmd_generate_rbt(d, 10, serv, grpc)

            did_config_list[c].append(d)

    # Quorum Config

    print("Create Quorum Config")

    create_quorum_config(
        did_config_list, 
        CLUSTERS, 
        QUORUM_NODES_PER_CLUSTER,
    )    

    # Initiate Transfer
    input("Start Transactions ?")
    intiate_transfer(did_config_list, CLUSTERS, QUORUM_NODES_PER_CLUSTER)

