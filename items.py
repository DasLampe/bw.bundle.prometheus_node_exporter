global node

version = node.metadata.get('prometheus_node_exporter').get('version')
checksum = node.metadata.get('prometheus_node_exporter').get('checksum_sha256')
symlink_dir = node.metadata.get('prometheus_node_exporter').get('directory')
actual_dir = f'/opt/node_exporter-{version}.linux-amd64'
user = node.metadata.get('prometheus_node_exporter').get('user')
group = node.metadata.get('prometheus_node_exporter').get('group')

groups = {
    group: {}
}

users = {
    user: {
        'gid': group,
        'home': symlink_dir,
        'password_hash': '*',
        'shell': '/sbin/nologin',
        'needs': [
            f'group:{group}',
        ]
    },
}

downloads = {
    f'/tmp/node_exporter-{version}.linux-amd64.tar.gz': {
        'url': 'https://github.com/prometheus/node_exporter/releases/download/'
               f'v{version}/node_exporter-{version}.linux-amd64.tar.gz',
        'sha256': checksum,
        'unless': f'test -f {actual_dir}/node_exporter',
    },
}

actions = {
    'unpack_node_exporter': {
        'command': f'tar xfvz /tmp/node_exporter-{version}.linux-amd64.tar.gz -C /opt',
        'needs': [
            f'download:/tmp/node_exporter-{version}.linux-amd64.tar.gz',
        ],
        'unless': f'test -d {actual_dir}',
    },
    'chown_node_exporter_dir': {
        'command': f'chown -R {user}:{group} {actual_dir}',
        'needs': [
            'action:unpack_node_exporter',
            f'user:{user}'
        ],
        'unless': f'test $(stat -c "%U:%G" {actual_dir}) = "{user}:{group}"'
    },
    'daemon_reload_node_exporter': {
        'command': 'systemctl daemon-reload',
        'triggered': True,
    }
}

files = {
    '/etc/systemd/system/node_exporter.service': {
        'source': 'etc/systemd/system/node_exporter.service.jinja2',
        'content_type': 'jinja2',
        'context': {
            'dir': symlink_dir,
            'user': user,
            'http': node.metadata.get('prometheus_node_exporter').get('http'),
        },
        'triggers': [
            'action:daemon_reload_node_exporter',
        ]
    },
    '/etc/systemd/system/node_exporter.socket': {
        'source': 'etc/systemd/system/node_exporter.socket.jinja2',
        'content_type': 'jinja2',
        'context': {
            'http': node.metadata.get('prometheus_node_exporter').get('http'),
        },
        'triggers': [
            'action:daemon_reload_node_exporter',
        ]
    },
}

symlinks = {
    f'{symlink_dir}': {
        'target': actual_dir,
        'needs': [
            'action:unpack_node_exporter',
        ],
    },
}

svc_systemd = {
    "node_exporter": {
        'running': True,
        'enabled': True,
        'needs': [
            f'symlink:{symlink_dir}',
            f'file:/etc/systemd/system/node_exporter.service',
            f'file:/etc/systemd/system/node_exporter.socket',
            f'action:unpack_node_exporter',
            f'user:{user}',
        ],
    },
}
