defaults = {
    'prometheus_node_exporter': {
        'version': '1.5.0',
        'checksum_sha256': 'af999fd31ab54ed3a34b9f0b10c28e9acee9ef5ac5a5d5edfdde85437db7acbb',
        'arch': 'amd64',
        'directory': '/opt/prometheus_node_exporter',
        'additional_interfaces': [],
        'http': {
            'addr': '0.0.0.0',
            'port': '9100',
        },
        'prometheus_ips': [],
        'user': 'node_exporter',
        'group': 'node_exporter',
    }
}

@metadata_reactor
def add_iptables(metadata):
    if not node.has_bundle("iptables"):
        raise DoNotRunAgain

    interfaces = ['main_interface']
    interfaces += metadata.get('prometheus_nod_exporter/additional_interfaces', [])

    iptables_rules = {}
    for interface in interfaces:
        for whitelistedIP in metadata.get('prometheus_node_exporter').get('prometheus_ips'):
            iptables_rules += repo.libs.iptables.accept(). \
                input(interface). \
                source(whitelistedIP). \
                tcp(). \
                dest_port(metadata.get('prometheus_node_exporter').get('http').get('port'))

    return iptables_rules