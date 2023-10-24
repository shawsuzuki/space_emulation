import configparser

template_service = """
  {name}_{index}:
    build:
      context: ./
      dockerfile: dockerfile/Dockerfile
    container_name: "{name}_{index}"
    networks:
      {name}_net:
        ipv6_address: {ip}
    ports:
      - "{external_port}:5001/tcp"
      - "{external_port}:5001/udp"
    tty: true
"""

template_network = """
  {name}_net:
    driver: bridge
    enable_ipv6: true
    ipam:
      config:
        - subnet: {subnet}/64
"""

def generate_docker_compose(filename="emulation_configure.config"):
    config = configparser.ConfigParser()
    config.read(filename)

    services = ""
    networks = ""

    subnet_changes = {
        "earth_surface": "fd00:1:85a3::",
        "earth_orbit": "fd00:2:85a3::",
        "moon_surface": "fd00:3:85a3::",
        "moon_orbit": "fd00:4:85a3::"
    }

    starting_port = 50100  # External starting port

    for section in config.sections():
        base_ip = subnet_changes[section]
        count = int(config[section]['衛星数'])

        for i in range(1, count+1):
            adjusted_ip = ":".join(base_ip.split(":")[:-1]) + f":{i}"
            services += template_service.format(
                name=section,
                index=i,
                ip=adjusted_ip,
                external_port=starting_port
            )
            starting_port += 1  # Increase external port number

        networks += template_network.format(name=section, subnet=base_ip)

    with open("docker-compose.yml", "w") as f:
        f.write("version: '3.8'\n")
        f.write("services:\n")
        f.write(services)
        f.write("networks:\n")
        f.write(networks)

if __name__ == "__main__":
    generate_docker_compose()
