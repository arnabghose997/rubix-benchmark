import subprocess
import os
import time
import requests
import platform
import re
import json
from concurrent.futures import ProcessPoolExecutor

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

def get_transfer_cmd_str(sender_address, receiver_address, rbt_amount, server_port, grpc_port):
    return f"./rubixgoplatform transferrbt -senderAddr {sender_address} -receiverAddr {receiver_address} -rbtAmount {rbt_amount} -port {server_port} -grpcPort {grpc_port}"

def cmd_rbt_transfer(cmd_string):
    os.chdir("./" + get_build_dir())
    start_time = time.time()
    output, code = run_command(cmd_string, True)
    print(output)
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)

    end_time = time.time()
    duration = end_time - start_time
    os.chdir("../")
    return output, duration

def intiate_transfer():
    # Make a list of transfer commands 
    commands = []
    base_server, base_grpc = get_base_ports()

    f = open('didconf.json', 'r')
    did_config = json.load(f)

    anchor = 6
    for i in range(1, GROUP_COUNT + 1):
        sender_serv = base_server + anchor
        sender_grpc = base_grpc + anchor

        receiver_serv = sender_serv + 1
    
        sender_did = did_config[str(sender_serv)]
        receiver_did = did_config[str(receiver_serv)]

        commands.append(get_transfer_cmd_str(sender_did, receiver_did, 1, sender_serv, sender_grpc))

        anchor += 7

    with ProcessPoolExecutor() as executor:
        # Use list comprehension to submit the command n times
        futures = [executor.submit(cmd_rbt_transfer, command) for command in commands]

    for f in futures:
        output, duration = f.result()
        print(f"Output '{output}' took {duration:.2f} seconds") 

intiate_transfer()
