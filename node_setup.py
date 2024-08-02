import subprocess
import os
import time
import requests
import platform

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

def get_list_of_non_runnable_nodes(n):
    for i in range(1, n+1):
        base_server, _ = get_base_ports()
        port = base_server + i
        url = f"http://localhost:{port}/api/getalldid"

        non_functional_nodes_port = []
        try:
            print(f"Sending GET request to URL: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                non_functional_nodes_port.append(port)
        except:
            non_functional_nodes_port.append(port)

    return non_functional_nodes_port

def check_if_nodes_is_running(server_idx):
    base_server, _ = get_base_ports()
    port = base_server + int(server_idx)
    print(f"Check if server with ENS web server port {port} is running...")
    url = f"http://localhost:{port}/api/getalldid"
    try:
        print(f"Sending GET request to URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Server with port {port} is running successfully")
        else:
            raise Exception(f"Failed with Status Code: {response.status_code} |  Server with port {port} is NOT running successfully")
    except:
        raise Exception(f"ConnectionError | Server with port {port} is NOT running successfully")


def run_n_nodes(n_nodes):
    for i in range(1, n_nodes+1):
        print("Running node " + str(i))
        cmd_run_rubix_servers("node" + str(i), i)


    time.sleep(40)

    s = get_list_of_non_runnable_nodes(n_nodes)
    print(s)

run_n_nodes(210)