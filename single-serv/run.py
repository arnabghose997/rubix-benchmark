import sys
import time
'''
Args:
    1 (int): to install prereq
'''

from tools.prerequisite import *
from tools.command import *
from tools.utils import get_base_ports, save_to_json, load_from_json
from tools.quorum import create_quorum_config
from tools.transfer import intiate_transfer
from tools.peer_details import add_peer_details_by_sender

TARGET_TRANSACTIONS = 100

QUORUM_DIDS = 7
NON_QUORUM_DID_PER_CLUSTER = 2 * TARGET_TRANSACTIONS

CLUSTERS = 2
CLUSTER_START_NODE_IDX = 9

TOTAL_DID_PER_CLUSTER = QUORUM_DIDS + int(NON_QUORUM_DID_PER_CLUSTER / CLUSTERS)
TOTAL_DID = TOTAL_DID_PER_CLUSTER * CLUSTERS
                                                
if __name__=='__main__':
    rerun_flag = -1
    if len(sys.argv) >= 2:
        rerun_flag = int(sys.argv[1])
    
    # Installing prereque
    print("Installing prereq")

    download_rubix_binary_tmp()
    download_ipfs_binary("Linux", "v0.21.0", "linux")
    generate_ipfs_swarm_key()

    # start Quorum Server
    print("Starting Quorum Server")
    for i in range(0, QUORUM_DIDS):
        node_idx = i
        base_serv, base_grpc = get_base_ports()
        
        serv, grpc = base_serv + node_idx, base_grpc + node_idx 
        node_name = "node" + str(node_idx)
        
        cmd_run_rubix_servers(node_name, node_idx)

    # Start Non Quorum Cluster
    for i in range(0, CLUSTERS):
        node_idx = CLUSTER_START_NODE_IDX + i
        base_serv, base_grpc = get_base_ports()
        
        serv, grpc = base_serv + node_idx, base_grpc + node_idx 
        node_name = "node" + str(node_idx)
        
        cmd_run_rubix_servers(node_name, node_idx)


    print("Wait for about 40 seconds and hit Enter")
    time.sleep(40)
    # create did

    print(f"Creating {TOTAL_DID} DIDs")
    
    '''
    {
        0: [did1, did2],
        1: [did3, did4]
    }
    '''
    did_config_list = {}

    # Quorum DIDS
    for c in range(QUORUM_DIDS):
        serv = base_serv + c
        grpc = base_grpc + c
        did_config_list[c] = []
  
        d = cmd_create_did(serv, grpc)
        cmd_generate_rbt(d, 100, serv, grpc)

        did_config_list[c].append(d)

    # Non Quorum DIDs
    for c in range(CLUSTERS):
        k = CLUSTER_START_NODE_IDX + c
        serv = base_serv + k
        grpc = base_grpc + k
        did_config_list[k] = []

        for _ in range(TOTAL_DID_PER_CLUSTER):    
            d = cmd_create_did(serv, grpc)
            cmd_generate_rbt(d, 2, serv, grpc)

            did_config_list[k].append(d)

    # Quorum Config
    print("Create Quorum Config")

    create_quorum_config(
        did_config_list,
        CLUSTERS,
        CLUSTER_START_NODE_IDX,
        QUORUM_DIDS,
    )    

    # Add peer details

    add_peer_details_by_sender(
        did_config_list,
        CLUSTERS,
        CLUSTER_START_NODE_IDX,
        QUORUM_DIDS,
    )

    # Initiate Transfer
    print("Start Transactions")
    intiate_transfer(did_config_list, CLUSTERS, CLUSTER_START_NODE_IDX, NON_QUORUM_DID_PER_CLUSTER)

