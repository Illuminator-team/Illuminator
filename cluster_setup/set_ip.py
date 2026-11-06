#!/usr/bin/env python3

import subprocess
import sys

def run_nmcli(args):
    """Run nmcli and return stdout; exit on error."""
    cmd = ["nmcli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running nmcli command:\n{result.stderr.strip()}")
        sys.exit(result.returncode)
    return result.stdout.strip()

def get_current_network_info(interface):
    """
    Extract first IPv4 address (with CIDR), default gateway, and DNS servers
    from `nmcli device show <interface>`.
    """
    output = run_nmcli(["device", "show", interface])
    info = {"ip_cidr": None, "gateway": None, "dns_servers": []}

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("IP4.ADDRESS[") or line.startswith("IP4.ADDRESS:"):
            parts = line.split(None, 1)
            if len(parts) > 1:
                ip_cidr = parts[1].split(":", 1)[-1].strip()
                info["ip_cidr"] = ip_cidr
        elif line.startswith("IP4.GATEWAY:"):
            info["gateway"] = line.split(":", 1)[1].strip()
        elif line.startswith("IP4.DNS[") or line.startswith("IP4.DNS:"):
            info["dns_servers"].append(line.split(":", 1)[1].strip())
    return info

def find_connection_for_interface(interface):
    """
    Return the name of the first NetworkManager connection bound to `interface`,
    or None if not found.
    """
    nmcli_output = run_nmcli(["-g", "NAME,DEVICE", "connection", "show"])
    for line in nmcli_output.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            conn_name, dev = parts
            if dev == interface:
                return conn_name
    return None

def convert_to_static_with_ip(interface, ip_cidr, gateway=None, dns_servers=None):
    """
    Convert the connection on `interface` to static with the given `ip_cidr`.
    If `gateway` or `dns_servers` are None, they’ll be omitted.
    """
    conn_name = find_connection_for_interface(interface)
    if not conn_name:
        print(f"Error: No NetworkManager connection is currently associated with '{interface}'.")
        print("Connect the interface first (DHCP), then rerun this script.")
        sys.exit(1)

    modify_args = [
        "connection", "modify", conn_name,
        "ipv4.addresses", ip_cidr,
        "ipv4.method", "manual"
    ]
    if gateway:
        modify_args += ["ipv4.gateway", gateway]
    if dns_servers:
        dns_str = ",".join(dns_servers)
        if dns_str:
            modify_args += ["ipv4.dns", dns_str]

    run_nmcli(modify_args)
    run_nmcli(["connection", "up", conn_name])

    print("\nStatic IPv4 configuration applied:")
    print(f"  Interface : {interface}")
    print(f"  Connection: {conn_name}")
    print(f"  IP/CIDR   : {ip_cidr}")
    print(f"  Gateway   : {gateway or '(none)'}")
    print(f"  DNS       : {dns_servers or '(none)'}\n")

def main():
    # Default interface is wlan0; change if you prefer a different default.
    interface = input("Network interface [wlan0]: ").strip() or "wlan0"

    # Pull current network info to use as defaults for GW/DNS.
    info = get_current_network_info(interface)
    if not info:
        print(f"Error: Could not read current network info for '{interface}'.")
        sys.exit(1)

    # Prompt for target IP/CIDR (required)
    print("Enter the static IPv4 address in CIDR notation, e.g. 192.168.1.50/24")
    ip_cidr = input("Static IP/CIDR: ").strip()
    if not ip_cidr or "/" not in ip_cidr:
        print("Error: You must provide an IPv4 address in CIDR form (e.g., 192.168.1.50/24).")
        sys.exit(1)

    # Offer to reuse the current gateway/DNS discovered via DHCP
    curr_gw = info.get("gateway")
    curr_dns_list = info.get("dns_servers") or []

    use_current_gw = "y"
    if curr_gw:
        use_current_gw = (input(f"Reuse current gateway [{curr_gw}]? [Y/n]: ").strip() or "y").lower()
    gateway = curr_gw if use_current_gw.startswith("y") else input("Gateway (leave blank for none): ").strip() or None

    use_current_dns = "y"
    if curr_dns_list:
        pretty_dns = ", ".join(curr_dns_list)
        use_current_dns = (input(f"Reuse current DNS servers [{pretty_dns}]? [Y/n]: ").strip() or "y").lower()
    if use_current_dns.startswith("y"):
        dns_servers = curr_dns_list
    else:
        raw = input("DNS servers (comma-separated, leave blank for none): ").strip()
        dns_servers = [x.strip() for x in raw.split(",") if x.strip()] if raw else None

    convert_to_static_with_ip(interface, ip_cidr, gateway=gateway, dns_servers=dns_servers)

if __name__ == "__main__":
    main()
