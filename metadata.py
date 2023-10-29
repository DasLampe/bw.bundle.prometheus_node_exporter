defaults = {
    'prometheus_node_exporter': {
        'version': '1.6.1',
        'checksum_sha256': 'ecc41b3b4d53f7b9c16a370419a25a133e48c09dfc49499d63bcc0c5e0cf3d01',
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
