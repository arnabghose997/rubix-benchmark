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

def cmd_add_peer_details(peer_id, did_id, did_type, server_port, grpc_port):
    os.chdir("./" + get_build_dir())
    cmd_string = f"./rubixgoplatform addpeerdetails -peerID {peer_id} -did {did_id} -didType {did_type} -port {server_port} -grpcPort {grpc_port}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform addpeerdetails -peerID {peer_id} -did {did_id} -didType {did_type} -port {server_port} -grpcPort {grpc_port}"
    output, code = run_command(cmd_string, True)
    print(output)

    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)

    os.chdir("../")
    return output


def add_peer_details_by_sender():
    f = open("didconf.json", "r")
    did_config = json.load(f)
    base_server, base_grpc = get_base_ports()

    anchor = 6
    for _ in range(1, GROUP_COUNT + 1):
        serv = base_server + anchor
        grpc = base_grpc + anchor

        did_id = did_config[str(serv)]
        peer_id = cmd_get_peer_id(serv, grpc)

        cmd_add_peer_details(peer_id, did_id, 4, serv, grpc)

        anchor += 7

add_peer_details_by_sender()
