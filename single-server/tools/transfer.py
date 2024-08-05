from .command import get_transfer_cmd_str, cmd_rbt_transfer
from concurrent.futures import ProcessPoolExecutor
from .utils import get_base_ports

def intiate_transfer(did_list, n_cluster, n_quorum_dids):
    # Make a list of transfer commands 
    commands = []
    base_serv, base_grpc = get_base_ports()

    for c in range(0, n_cluster):
        serv = base_serv + c
        grpc = base_grpc + c

        sender_did = did_list[c][n_quorum_dids]
        receiver_did = did_list[c][n_quorum_dids+1]

        commands.append(get_transfer_cmd_str(sender_did, receiver_did, 1, serv, grpc))

    with ProcessPoolExecutor() as executor:
        # Use list comprehension to submit the command n times
        futures = [executor.submit(cmd_rbt_transfer, command) for command in commands]

    for f in futures:
        output = f.result()
