from .command import cmd_add_peer_details, cmd_get_peer_id
from .utils import get_base_ports

def add_peer_details_by_sender(did_config, clusters, cluster_start_idx, n_quorum_dids):
    base_serv, base_grpc = get_base_ports()

    for k in range(clusters):
        serv = base_serv + cluster_start_idx + k
        grpc = base_grpc + cluster_start_idx + k

        for c in range(0, n_quorum_dids):
            did_id = did_config[c][0]
            q_serv = base_serv + c
            q_grpc = base_grpc + c
            peer_id = cmd_get_peer_id(q_serv, q_grpc)

            cmd_add_peer_details(peer_id, did_id, 4, serv, grpc)
