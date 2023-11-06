import configparser
import ipaddress
from pathlib import Path
import yaml

# Configファイルを読み込む
config_path = Path.cwd() / 'input' / 'emulation.config'
config = configparser.ConfigParser()
config.read(config_path)

# 各ネットワークごとのIPアドレス割り当てのカウンターを設定
network_ip_counters = {}

# ネットワークとサービスの設定を構築
networks = {}
services = {}
host_port = 50000  # ホストポートの開始番号

# 全てのセクションのサブネットを事前に設定しておく
for section in config.sections():
    network_name = f"{section}_network"
    subnet = config.get(section, 'IPv4_address')
    networks[network_name] = {
        'ipam': {
            'config': [{'subnet': subnet}]
        }
    }
    # 各サブネットの24ビット目が1の最初のホストアドレスをカウンターに設定
    subnet_base = ipaddress.ip_network(subnet)
    first_ip = ipaddress.IPv4Address(int(subnet_base.network_address+1) | (1 << 8))
    network_ip_counters[network_name] = first_ip

# セクションごとにサービスを設定
for section in config.sections():
    network_name = f"{section}_network"
    num_satellite = config.getint(section, 'num_satellite')

    for i in range(1, num_satellite + 1):
        service_name = f"{section}_{i}"
        container_name = service_name
        host_port += 1  # ホストポートをインクリメント

        service_networks = {}

        # 全ネットワークに対してサービスを登録し、IPアドレスを割り当てる
        for net_name, counter in network_ip_counters.items():
            service_networks[net_name] = {
                'ipv4_address': str(counter)
            }
            # 各ネットワークカウンターをインクリメント
            network_ip_counters[net_name] = ipaddress.IPv4Address(int(counter) + 1)

        # サービス設定を追加
        services[service_name] = {
            'build': {
                'context': './',
                'dockerfile': './input/Dockerfile',
            },
            'container_name': container_name,
            'networks': service_networks,
            'ports': [f"{host_port}:5001"],
            'privileged': True,
            'tty': True,
        }

# docker-composeファイル用のデータ構造
docker_compose_data = {
    'version': '3.8',
    'services': services,
    'networks': networks,
}

# YAMLファイルとしてdocker-compose.ymlを書き出し
with open('docker-compose.yml', 'w') as file:
    yaml.dump(docker_compose_data, file, default_flow_style=False)

print('docker-compose.yml has been generated.')
