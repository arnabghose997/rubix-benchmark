from .command import get_transfer_cmd_str, cmd_rbt_transfer
from concurrent.futures import ProcessPoolExecutor
from .utils import get_base_ports

def intiate_transfer(did_list, n_cluster, cluster_start_idx, n_non_quorum_dids):
    # Make a list of transfer commands 
    commands = []
    base_serv, base_grpc = get_base_ports()

    for c in range(0, n_cluster):
        k = cluster_start_idx + c
        serv = base_serv + k
        grpc = base_grpc + k

        for q in range(0, n_non_quorum_dids, 2):
            sender_did = did_list[k][q]
            receiver_did = did_list[k][q+1]

            commands.append(get_transfer_cmd_str(sender_did, receiver_did, 1, serv, grpc))

    with ProcessPoolExecutor() as executor:
        # Use list comprehension to submit the command n times
        futures = [executor.submit(cmd_rbt_transfer, command) for command in commands]

    for f in futures:
        output = f.result()
