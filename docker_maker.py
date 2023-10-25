import configparser
import yaml
import ipaddress

CONFIG_FILE = 'emulation_configure.config'
OUTPUT_FILE = 'docker-compose.yml'

def generate_docker_compose():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    services = {}
    base_port = 50000

    for idx, section in enumerate(config.sections()):
        start_ipv4 = config.get(section, 'IPv4開始アドレス')
        sat_num = config.getint(section, '衛星数')

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
                        'ipv4_address': str(ipaddress.ip_address(start_ipv4) + i - 1)
                    }
                },
                'ports': [
                    f"{port}:5001/tcp",
                    f"{port}:5001/udp"
                ],
                'tty': True
            }

            services[service_name] = service

        base_port += sat_num  # この行を追加


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
    docker_compose = generate_docker_compose()
    with open(OUTPUT_FILE, 'w') as file:
        # Save yaml data
        yaml_data = yaml.dump(docker_compose, default_flow_style=False, sort_keys=False)
        file.write(yaml_data)

if __name__ == "__main__":
    main()
