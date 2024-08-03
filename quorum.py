import subprocess
import os
import time
import requests
import platform
import re
import json

NODE_COUNT = 21
GROUP_COUNT = int(NODE_COUNT / 7)

def get_build_dir():
    os_name = platform.system()
    build_folder = ""
    if os_name == "Linux":
        build_folder = "linux"
    elif os_name == "Windows":
        build_folder = "windows"
    elif os_name == "Darwin":
        build_folder = "mac"

    return build_folder

def get_base_ports():
    base_ens_server = 20000
    base_grpc_port = 10500

    return base_ens_server, base_grpc_port

def is_windows_os():
    os_name = platform.system()
    return os_name == "Windows"

def run_command(cmd_string, is_output_from_stderr=False):
    assert isinstance(cmd_string, str), "command must be of string type"
    cmd_result = subprocess.run(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    code = cmd_result.returncode
    
    if int(code) != 0:
        print("Failed at: ", cmd_result)
        return

    output = ""
    if not is_output_from_stderr:
        output = cmd_result.stdout.decode('utf-8')[:-1]
        print(output)
        if output.find('[ERROR]') > 0 or output.find('parse error') > 0:
            return output, 1
        else:
            return output, code
    else:
        output = cmd_result.stderr.decode('utf-8')[:-1]
        if output.find('[ERROR]') > 0 or output.find('parse error') > 0:
            print(output)
            return output, 1
        else:
            return output, code
        

def cmd_get_peer_id(server_port, grpc_port):
    os.chdir("./" + get_build_dir())
    cmd_string = f"./rubixgoplatform get-peer-id -port {server_port} -grpcPort {grpc_port}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform get-peer-id -port {server_port} -grpcPort {grpc_port}"
    output, code = run_command(cmd_string)

    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)
    os.chdir("../")
    return output


def cmd_add_quorum_dids(server_port, grpc_port, quorumlist = "quorumlist.json"):
    os.chdir("./" + get_build_dir())
    cmd_string = f"./rubixgoplatform addquorum -port {server_port} -grpcPort {grpc_port} -quorumList {quorumlist}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform addquorum -port {server_port} -grpcPort {grpc_port} -quorumList {quorumlist}"
    output, code = run_command(cmd_string, True)
    print(output)
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)

    os.chdir("../")
    return output

def cmd_setup_quorum_dids(did, server_port, grpc_port):
    os.chdir("./" + get_build_dir())
    cmd_string = f"./rubixgoplatform setupquorum -did {did} -port {server_port} -grpcPort {grpc_port}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform setupquorum -did {did} -port {server_port} -grpcPort {grpc_port}"
    output, code = run_command(cmd_string, True)
    print(output)
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)

    os.chdir("../")
    return output


def create_quorum_config():
    f = open("didconf.json", 'r')
    did_config: dict = json.load(f)
    base_server, base_grpc = get_base_ports()

    # Create groupwise quorumlist
    anchor = 1
    for g in range(1, GROUP_COUNT + 1):
        j = anchor
        quorumlistconfig = []
        quorum_file_name = "quorumlist_" + str(g) + ".json"
        
        nq_anchor = 0
        for q in range(j, j+5):
            qlistconf = {
                "type": 2,
                "address": did_config[str(base_server + q)]
            }
            quorumlistconfig.append(qlistconf)
            cmd_setup_quorum_dids(did_config[str(base_server + q)], base_server + q, base_grpc + q)
            
        nq_anchor = anchor + 5
        anchor += 7 

        with open("linux/" + quorum_file_name, "w") as f:
            json.dump(quorumlistconfig, f)

        k = nq_anchor
        for s in range(k, k+2):
            cmd_add_quorum_dids(base_server + s, base_grpc + s, quorum_file_name)


    # Setup Quorum
    # anchor = 1
    # for i in range(1, GROUP_COUNT + 1):
    #     j = anchor
    #     for q in range(j, j + 5):
    #         cmd_setup_quorum_dids(did_config[str(base_server + q)], base_server + q, base_grpc + q)
    #     anchor += 7


create_quorum_config()