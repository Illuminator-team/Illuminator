#!/usr/bin/env python3

import subprocess
import sys

def run_nmcli(args):
    """
    Run nmcli with the given list of arguments. 
    Returns the command's stdout on success, or exits on error.
    """
    cmd = ["nmcli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running nmcli command:\n{result.stderr.strip()}")
        sys.exit(result.returncode)
    return result.stdout.strip()

def get_current_network_info(interface):
    """
    Parses `nmcli device show <interface>` to extract the first IPv4 address (with CIDR),
    the default gateway, and all DNS servers. 
    Returns a dict with keys: 'ip_cidr', 'gateway', 'dns_servers'.
    
    If no info is found, returns None or an empty dict for missing fields.
    """
    output = run_nmcli(["device", "show", interface])
    
    info = {
        "ip_cidr": None,
        "gateway": None,
        "dns_servers": []
    }
    
    # Example lines we want to parse:
    # IP4.ADDRESS[1]:                         192.168.1.101/24
    # IP4.GATEWAY:                            192.168.1.1
    # IP4.DNS[1]:                             8.8.8.8
    # IP4.DNS[2]:                             8.8.4.4
    
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("IP4.ADDRESS[") or line.startswith("IP4.ADDRESS:"):
            # e.g. "IP4.ADDRESS[1]: 192.168.1.101/24"
            parts = line.split(None, 1)
            if len(parts) > 1:
                # The second part after the colon is usually the IP/CIDR
                ip_cidr = parts[1].split(":")[-1].strip()  # remove "IP4.ADDRESS[n]:" if present
                info["ip_cidr"] = ip_cidr
        elif line.startswith("IP4.GATEWAY:"):
            # e.g. "IP4.GATEWAY: 192.168.1.1"
            gateway = line.split(":", 1)[1].strip()
            info["gateway"] = gateway
        elif line.startswith("IP4.DNS[") or line.startswith("IP4.DNS:"):
            # e.g. "IP4.DNS[1]: 8.8.8.8"
            dns_value = line.split(":", 1)[1].strip()
            info["dns_servers"].append(dns_value)
    
    return info

def find_connection_for_interface(interface):
    """
    Returns the name of the first NetworkManager connection currently associated
    with the given interface, or None if no match is found.
    """
    nmcli_output = run_nmcli(["-g", "NAME,DEVICE", "connection", "show"])
    lines = nmcli_output.splitlines()
    
    for line in lines:
        parts = line.split(":")
        if len(parts) == 2:
            conn_name, dev = parts
            if dev == interface:
                return conn_name
    return None

def create_connection(interface, connection_name):
    """
    Creates a new NetworkManager connection for the given interface
    with the specified connection name (initially DHCP).
    """
    run_nmcli([
        "connection", "add",
        "type", "wifi",
        "ifname", interface,
        "con-name", connection_name,
        "ssid", "YOUR_WIFI_SSID_HERE"   # placeholder if it’s a Wi-Fi connection
    ])
    # If needed, you can also set Wi-Fi security (e.g., WPA2) here with:
    #   "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", "YOUR_PASSWORD"
    # but that depends on your actual Wi-Fi setup.

def convert_to_static(interface):
    # 1. Gather current DHCP configuration
    info = get_current_network_info(interface)
    if not info or not info["ip_cidr"]:
        print(f"Error: Could not find a valid IP for {interface}. Is it currently up with DHCP?")
        sys.exit(1)
    
    ip_cidr     = info["ip_cidr"]
    gateway     = info["gateway"]
    dns_servers = info["dns_servers"]
    
    if not gateway:
        print("Warning: No default gateway found. The static config will have no 'gateway'.")
    if not dns_servers:
        print("Warning: No DNS servers found. The static config will have no 'dns_servers'.")
    
    # 2. Find or create a connection for this interface
    conn_name = find_connection_for_interface(interface)
    if not conn_name:
        conn_name = f"static-{interface}"
        print(f"No connection found for {interface}; creating connection '{conn_name}'...")
        create_connection(interface, conn_name)
    else:
        print(f"Found existing connection '{conn_name}' for interface '{interface}'.")

    # 3. Convert the connection to static
    dns_str = ",".join(dns_servers)
    modify_args = [
        "connection", "modify", conn_name,
        "ipv4.addresses", ip_cidr,
        "ipv4.method", "manual"
    ]
    # Add gateway if present
    if gateway:
        modify_args += ["ipv4.gateway", gateway]
    # Add DNS if present
    if dns_str:
        modify_args += ["ipv4.dns", dns_str]
    
    run_nmcli(modify_args)

    # 4. Bring up the connection
    run_nmcli(["connection", "up", conn_name])
    
    print(f"\nConversion to static IP complete for {interface}.\n"
          f"IP: {ip_cidr}, Gateway: {gateway}, DNS: {dns_servers}.\n")

def main():
    interface = "wlan0"  # As requested
    convert_to_static(interface)

if __name__ == "__main__":
    main()
