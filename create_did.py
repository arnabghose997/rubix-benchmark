import subprocess
import os
import time
import requests
import platform
import re
import json

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

def cmd_create_did(server_port, grpc_port, did_type = 4):
    os.chdir("./" + get_build_dir())

    cmd_string = f"./rubixgoplatform createdid -port {server_port} -grpcPort {grpc_port} -didType {did_type}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform createdid -port {server_port} -grpcPort {grpc_port} -didType {did_type}"
    output, code = run_command(cmd_string, True)
    print(output)
    
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)
    
    did_id = ""
    if "successfully" in output:
        pattern = r'bafybmi\w+'
        matches = re.findall(pattern, output)
        if matches:
            did_id = matches[0]
        else:
            raise Exception("unable to extract DID ID")

    os.chdir("../")
    return did_id

def create_and_config_did():
    base_serv_port, base_gprc_port = get_base_ports()
    config_map = {}

    for i in range(1, 106):
        serv_port = base_serv_port + i
        grpc_port = base_gprc_port + i

        did_res = cmd_create_did(serv_port, grpc_port)
        config_map[str(serv_port)] = did_res

    print(config_map)

    with open("./didconf.json", 'w') as f:
        json.dump(config_map, f, indent=4)

create_and_config_did()