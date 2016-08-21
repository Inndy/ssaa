#!/usr/bin/env python3

import os

def run(*args):
    os.execlp(args[0], *args)

rsa_key_size = int(os.getenv('RSA_KEY_SIZE', 4096))
cert_days = int(os.getenv('CERT_DAYS', 365))

run('openssl', 'req', '-new', '-newkey', 'rsa:%d' % rsa_key_size,
    '-days', str(cert_days), '-nodes', '-x509', '-keyout',
    'server.key', '-out', 'server.crt')

os.chmod('server.key', 0o600)
