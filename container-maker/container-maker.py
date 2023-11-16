import yaml
import configparser
from itertools import combinations

# Function to load and parse the configuration file
def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return {section: dict(config.items(section)) for section in config.sections()}

# Function to create subnet strings
def create_subnet_string(index):
    return f"172.0.{index}.0/24"

# Function to generate nftables.sh script
def generate_nftables_script(containers):
    script_lines = ["#!/bin/bash"]
    for container in containers:
        for x in range(len(containers) - 1):
            for y in range(x + 1, len(containers)):
                script_lines.append(f"docker exec -it {container} iptables -A FORWARD -i en{x} -o en{y} -j ACCEPT")
                script_lines.append(f"docker exec -it {container} iptables -A FORWARD -i en{y} -o en{x} -j ACCEPT")

    with open('nftables.sh', 'w') as file:
        file.write('\n'.join(script_lines))
        
# Load the configuration from the input directory
config = load_config('../input/emulation.config')

# Parse the number of satellites from config and create a list of containers
satellites = {sat: int(details['num_satellite']) for sat, details in config.items()}
containers = [f"{sat}{i+1}" for sat, num in satellites.items() for i in range(num)]

# Create all possible pairs for the networks
network_pairs = list(combinations(containers, 2))

# Initialize network configurations
networks = {}
subnet_index = 1

for pair in network_pairs:
    # Create a network name based on the sorted pair of container names
    network_name = "_".join(sorted(pair)) + "_network"
    networks[network_name] = {
        'ipam': {
            'config': [{'subnet': create_subnet_string(subnet_index)}]
        }
    }
    subnet_index += 1

# Initialize a dictionary to track the last assigned IP address for each network
last_ip_addresses = {network: 2 for network in networks}

# Initialize service configurations
services = {}
port_counter = 50000  # Start assigning ports from 50000

for container in containers:
    # Calculate connected networks based on the existing network pairs
    connected_networks = {
        "_".join(sorted([container, other])) + "_network"
        for other in containers if container != other
    }
    # Sort networks to ensure consistent IP assignment
    sorted_networks = sorted(connected_networks)

    # Each container's network config with unique IP address assignment
    network_config = {}
    for network in sorted_networks:
        subnet_parts = networks[network]['ipam']['config'][0]['subnet'].split('.')
        # Increment the last IP for this network
        last_ip = last_ip_addresses[network]
        base_ip = f"{subnet_parts[0]}.{subnet_parts[1]}.{subnet_parts[2]}.{last_ip}"
        network_config[network] = {'ipv4_address': base_ip}
        # Increment the IP address for the next assignment in this network
        last_ip_addresses[network] += 1

    # Each container's complete config including ports
    services[container] = {
        'build': {
            'context': '.',
            'dockerfile': './container-maker/Dockerfile',
        },
        'container_name': container,
        'networks': network_config,
        'ports': [f"{port_counter}:{5001}"],
        'privileged': True,
        'tty': True
    }
    port_counter += 1  # Increment the port counter for the next container


# Docker-compose structure
docker_compose_structure = {
    'version': '3.7',
    'services': services,
    'networks': networks
}

# Write the docker-compose structure to a file
docker_compose_file = '../docker-compose.yml'
with open(docker_compose_file, 'w') as file:
    yaml.dump(docker_compose_structure, file, default_flow_style=False)

print(f"{docker_compose_file} has been generated.")
