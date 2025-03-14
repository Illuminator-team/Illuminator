#!/usr/bin/env python3

import os
import subprocess
import sys
import getpass
import shutil

def generate_ssh_key(key_path):
    """
    Generate an ed25519 SSH key pair.
    """
    print(f"[*] Generating new SSH key pair at: {key_path}")
    try:
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", ""],
            check=True
        )
        print("[+] SSH key pair generated successfully.")
    except subprocess.CalledProcessError:
        print("[!] Error generating SSH key.")
        sys.exit(1)

def copy_ssh_key(user, host, key_pub_path):
    """
    Copy the public key to the server using ssh-copy-id if available.
    Otherwise, manually copy the key by SSHing and appending to authorized_keys.
    """
    ssh_copy_id_path = shutil.which("ssh-copy-id")
    if ssh_copy_id_path:
        print("[*] Attempting to copy key using ssh-copy-id.")
        try:
            subprocess.run(
                [ssh_copy_id_path, "-i", key_pub_path, f"{user}@{host}"],
                check=True
            )
            print("[+] Public key copied using ssh-copy-id.")
            return
        except subprocess.CalledProcessError:
            print("[!] ssh-copy-id failed. Will attempt manual copy.")
    
    # Fallback: manual copy
    print("[*] Copying key manually.")
    
    # Read public key
    try:
        with open(key_pub_path, "r") as f:
            public_key = f.read().strip()
    except FileNotFoundError:
        print("[!] Public key file not found.")
        sys.exit(1)

    # Append public key to authorized_keys on server
    try:
        print("[*] Connecting to server to append key...")
        # Create .ssh directory if it doesn't exist
        create_ssh_dir_cmd = f"mkdir -p ~/.ssh && chmod 700 ~/.ssh"
        subprocess.run(["ssh", f"{user}@{host}", create_ssh_dir_cmd], check=True)

        # Append to authorized_keys
        append_key_cmd = f'echo "{public_key}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
        subprocess.run(["ssh", f"{user}@{host}", append_key_cmd], check=True)

        print("[+] Public key appended manually to authorized_keys on server.")
    except subprocess.CalledProcessError:
        print("[!] Failed to manually copy SSH key to server.")
        sys.exit(1)


def test_ssh_connection(user, host):
    """
    Test if SSHing to the server works without a password by running a simple command.
    """
    print("[*] Testing passwordless SSH connection...")
    try:
        # The -o BatchMode=yes causes SSH to fail quickly if a password is needed.
        subprocess.run(
            ["ssh", "-o", "BatchMode=yes", f"{user}@{host}", "echo", "Success!"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("[+] Passwordless SSH connection succeeded.")
    except subprocess.CalledProcessError:
        print("[!] Passwordless SSH connection failed.")
        print("    Double-check the server's SSH settings, your key, or any firewall issues.")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <host>")
        sys.exit(1)

    user = sys.argv[1]
    host = sys.argv[2]

    # SSH key paths
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)

    key_path = os.path.join(ssh_dir, "id_ed25519")
    key_pub_path = key_path + ".pub"

    # 1. Check if SSH key pair exists
    if not os.path.isfile(key_path) or not os.path.isfile(key_pub_path):
        generate_ssh_key(key_path)
    else:
        print("[*] SSH key pair already exists. Skipping generation.")

    # 2. Copy the public key to the server
    copy_ssh_key(user, host, key_pub_path)

    # 3. Test the SSH connection
    test_ssh_connection(user, host)

    print("\nAll done! You should now be able to SSH without a password.")

if __name__ == "__main__":
    main()
