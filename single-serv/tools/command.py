import subprocess
import os
from .utils import get_build_dir, get_base_ports, is_windows_os
import re

def run_command(cmd_string, is_output_from_stderr=False):
    assert isinstance(cmd_string, str), "command must be of string type"
    cmd_result = subprocess.run(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    code = cmd_result.returncode
    
    if int(code) != 0:
        err_output = cmd_result.stderr.decode('utf-8')[:-1]
        print(err_output)
        return err_output, int(code)

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

def cmd_run_rubix_servers(node_name, server_port_idx):
    os.chdir("./" + get_build_dir())
    
    base_node_server, base_grpc_port = get_base_ports()
    grpc_port = base_grpc_port + server_port_idx
    node_server = base_node_server + server_port_idx

    cmd_string = ""
    if is_windows_os():
        cmd_string = f"powershell -Command  Start-Process -FilePath '.\\rubixgoplatform.exe' -ArgumentList 'run -p {node_name} -n {server_port_idx} -s -testNet -grpcPort {grpc_port}' -WindowStyle Hidden"
    else:
        cmd_string = f"tmux new -s {node_name} -d ./rubixgoplatform run -p {node_name} -n {server_port_idx} -s -testNet -grpcPort {grpc_port}"
    
    _, code = run_command(cmd_string)
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)
    
    os.chdir("../")
    return node_server, grpc_port

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


def get_transfer_cmd_str(sender_address, receiver_address, rbt_amount, server_port, grpc_port):
    return f"./rubixgoplatform transferrbt -senderAddr {sender_address} -receiverAddr {receiver_address} -rbtAmount {rbt_amount} -port {server_port} -grpcPort {grpc_port}"

def cmd_rbt_transfer(cmd_string):
    s = os.getcwd()
    if s != "/mnt/d/benchmarking/lab/single-serv/linux":
        os.chdir("/mnt/d/benchmarking/lab/single-serv/linux")

    output, code = run_command(cmd_string, True)

    return output

def cmd_generate_rbt(did_id, numTokens, server_port, grpc_port):
    os.chdir("./" + get_build_dir())
    cmd_string = f"./rubixgoplatform generatetestrbt -did {did_id} -numTokens {numTokens} -port {server_port} -grpcPort {grpc_port}"
    if is_windows_os():
        cmd_string = f".\\rubixgoplatform generatetestrbt -did {did_id} -numTokens {numTokens} -port {server_port} -grpcPort {grpc_port}"
    output, code = run_command(cmd_string, True)
    
    if code != 0:
        raise Exception("Error occurred while run the command: " + cmd_string)

    os.chdir("../")
    return output