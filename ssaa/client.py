import getpass
import os
import socket
import ssl
import sys

import sockutils
import authenticator

try:
    import config
except ImportError:
    class config:
        user = ''
        secret = ''
    print('''\
Tips: you can put your username and secert in config.py
Example:

user = 'inndy'
secret = 'helloworld'
''')

try:
    connect_pair = (sys.argv[1], int(sys.argv[2]))
except IndexError:
    print('Usage: python3 %s ip port' % sys.argv[0])
    exit()

username = config.user or input('User: ').strip()
secret = config.secret or getpass.getpass('Secret: ')

def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(connect_pair)
    except:
        print('[client] Connect failed')
        return False

    try:
        sock = ssl.wrap_socket(
                sock,
                ca_certs='key/server.crt',
                cert_reqs=ssl.CERT_REQUIRED,
                ssl_version=ssl.PROTOCOL_TLSv1_2,
                ciphers='ECDHE-RSA-AES256-GCM-SHA384'
                )
    except ssl.SSLError:
        print('[client] Server has wrong certificate, please check '
                'configuration or you are suffer from MITM attacked!')
        return False

    sockutils.sendstring_to_socket(sock, username.encode('utf-8'))
    session = sockutils.recvstring_from_socket(sock)

    proof = authenticator.calc_proof(session, secret.encode('utf-8'))
    sockutils.sendstring_to_socket(sock, proof)

    check_passed = sock.recv(1) == b'1'

    if not check_passed:
        print('[client] Login failed, please check your username and secret')
        exit(1)

    print('[client] Login success as user %s' % username)
    return sock

bind_ip = '127.0.0.1'
bind_port = 25565
bind_pair = (bind_ip, bind_port)

print('[client] bind on %s:%d' % bind_pair)
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv_sock.bind(bind_pair)
serv_sock.listen(5)

while True:
    incoming_sock, addr = serv_sock.accept()

    print('[client] connection from', addr)
    remote_sock = connect()
    if not remote_sock:
        print('[client] connect to remote failed')
        incoming_sock.close()
        continue

    sockutils.binding_socket_pipe(incoming_sock, remote_sock)
