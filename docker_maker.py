# Version: 1.1
import configparser
import yaml
import ipaddress

CONFIG_FILE = 'emulation.config'
OUTPUT_FILE = 'docker-compose.yml'

def generate_docker_compose():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    services = {}
    base_port = 50000
    used_ip_ranges = []

    for idx, section in enumerate(config.sections()):
        ipv4_cidr = config.get(section, 'IPv4アドレス')
        sat_num = config.getint(section, '衛星数')
        
        network = ipaddress.ip_network(ipv4_cidr, strict=False)

        # エラーチェック1: 利用可能なIPアドレス数が足りるか確認
        if len(list(network.hosts())) < sat_num:
            raise ValueError(f"{section}のIPアドレス範囲{ipv4_cidr}は要求されるコンテナ数{sat_num}に対して不足しています。")
        
        # エラーチェック2: 既に使用されたIPアドレス範囲との重複確認
        for used_range in used_ip_ranges:
            if network.overlaps(used_range):
                raise ValueError(f"{section}のIPアドレス範囲{ipv4_cidr}は既に使用されています。")
        
        used_ip_ranges.append(network)

        current_ip = network.network_address + 1  # start from the first usable IP

        for i in range(1, sat_num + 1):
            service_name = f"{section}_{i}"
            port = base_port + i

            service = {
                'build': {
                    'context': './',
                    'dockerfile': 'dockerfile/Dockerfile'
                },
                'container_name': service_name,
                'networks': {
                    'fixed_compose_network': {
                        'ipv4_address': str(current_ip)
                    }
                },
                'ports': [
                    f"{port}:5001/tcp",
                    f"{port}:5001/udp"
                ],
                'tty': True,
                'privileged': True
            }
            services[service_name] = service
            current_ip += 1  # increment the IP address for the next container

        base_port += sat_num

    return {
        'version': '5.1',
        'services': services,
        'networks': {
            'fixed_compose_network': {
                'ipam': {
                    'driver': 'default',
                    'config': [{
                        'subnet': '172.20.0.0/16'
                    }]
                }
            }
        }
    }

def main():
    try:
        docker_compose = generate_docker_compose()
        with open(OUTPUT_FILE, 'w') as file:
            yaml_data = yaml.dump(docker_compose, default_flow_style=False, sort_keys=False)
            file.write(yaml_data)
    except ValueError as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()
