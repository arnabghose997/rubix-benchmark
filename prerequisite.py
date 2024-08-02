import requests
import os
import shutil
import binascii
import tarfile

def download_rubix_binary():
    if not os.path.exists("linux"):
        os.makedirs("linux")

    download_url = "https://github.com/rubixchain/rubixgoplatform/releases/download/v0.0.18/rubixgoplatform-v0.0.18-linux-amd64.tar.gz"
    
    download_path = "rubixgoplatform-v0.0.18-linux-amd64.tar.gz"
    print("Downloading Rubix binary...")
    response = requests.get(download_url)
    with open(download_path, "wb") as f:
        f.write(response.content)
    print("Download completed.")
    
    # Path to the tar.gz file
    # The specific file you want to extract
    file_to_extract = 'rubixgoplatform'
    # Path where you want to save the extracted file
    output_path = 'linux/rubixgoplatform'

    # Open the tar.gz file
    with tarfile.open(download_path, 'r:gz') as tar:
        # Extract the specific file
        extracted_file = tar.extractfile(file_to_extract)
        
        if extracted_file is not None:
            # Save the extracted file to the desired output path
            with open(output_path, 'wb') as f:
                f.write(extracted_file.read())
        else:
            print(f"File {file_to_extract} not found in the archive")

    os.remove(download_path)

def download_ipfs_binary(os_name, version, build_dir):
    download_url = ""
    
    if os_name == "Linux":
        download_url = f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_linux-amd64.tar.gz"
    elif os_name == "Windows":
        download_url = f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_windows-amd64.zip"
    elif os_name == "Darwin":  # MacOS
        download_url = f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_darwin-amd64.tar.gz"
    else:
        raise ValueError("Unsupported operating system")

    # Download the IPFS binary archive
    download_path = f"kubo_{version}_{os_name.lower()}-amd64.tar.gz" if os_name != "Windows" else f"kubo_{version}_{os_name.lower()}-amd64.zip"
    print("Downloading IPFS binary...")
    response = requests.get(download_url)
    with open(download_path, "wb") as f:
        f.write(response.content)
    print("Download completed.")

    # Extract the archive
    print("Extracting IPFS binary...")
    if os_name == "Windows":
        # For Windows, we need to use the 'zipfile' module to extract
        import zipfile
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            zip_ref.extractall("kubo")
    else:
        # For Linux and MacOS, we use tar
        import tarfile
        with tarfile.open(download_path, "r:gz" if os_name != "Darwin" else "r") as tar_ref:
            tar_ref.extractall("kubo")
    print("Extraction completed.")

    # Check the contents of the kubo directory
    print("Contents of kubo directory:")
    for item in os.listdir("kubo"):
        print(item)

    # Move IPFS binary to the appropriate folder
    print("Moving IPFS binary...")
    
    ipfs_bin_name = "ipfs"
    if os_name == "Windows":
        ipfs_bin_name = "ipfs.exe"

    src_file = os.path.join("kubo", "kubo", ipfs_bin_name)
    dest_dir = os.path.join(build_dir, ipfs_bin_name)
    
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    if os.path.exists(src_file):
        shutil.move(src_file, dest_dir)
        print("IPFS binary moved to", dest_dir)

        # Check if the file is present at the destination
        dest_file = os.path.join(dest_dir)
        if not os.path.exists(dest_file):
            raise FileNotFoundError("IPFS binary not found at the destination after move operation.")
    else:
        raise FileNotFoundError("Installed IPFS binary file does not exist.")

    # Clean up
    os.remove(download_path)
    shutil.rmtree("kubo")
    print("\nIPFS has been installed succesfully.")


def generate_ipfs_swarm_key():
    try:
        key = os.urandom(32)
    except Exception as e:
        print("While trying to read random source:", e)
        return

    output = "/key/swarm/psk/1.0.0/\n/base16/\n" + binascii.hexlify(key).decode()

    directory = "./linux"
    filename = f"{directory}/testswarm.key"

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, "w") as file:
        file.write(output)

download_rubix_binary()
download_ipfs_binary("Linux", "v0.21.0", "linux")
generate_ipfs_swarm_key()
