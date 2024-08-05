# from .command import cmd_add_peer_details

# def add_peer_details_by_sender(did_list, n_cluster, n_quorum_dids, n_non_quorum_dids, serv, grpc):
#     anchor = 7
#     for _ in range(0, n_cluster):

#         did_id = did_config[str(serv+1)]
#         peer_id = cmd_get_peer_id(serv+1, grpc+1)

#         cmd_add_peer_details(peer_id, did_id, 4, serv, grpc)

#         #Add quorums
#         for x in range(5, 0, -1):
#             idx = anchor - x

#             q_serv = base_server + idx
#             q_grpc = base_grpc + idx

#             did_id = did_config[str(q_serv)]
#             peer_id = cmd_get_peer_id(q_serv, q_grpc)

#             cmd_add_peer_details(peer_id, did_id, 4, serv, grpc)
#         anchor += 7