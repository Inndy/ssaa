import os
import socket
import ssl
import threading

import sockutils
import authenticator

DEFAULT_BIND_IP = '0.0.0.0'
DEFAULT_PORT = 25564
DEFAULT_TARGET_PORT = 25565

def auth_routine(sock):
    user = sockutils.recvstring_from_socket(sock)
    if not user:
        return False
    random_bytes = os.urandom(16)
    sockutils.sendstring_to_socket(sock, random_bytes)
    proof = sockutils.recvstring_from_socket(sock)
    return authenticator.auth(random_bytes, user, proof)

bind_ip = os.getenv('BIND', DEFAULT_BIND_IP)
bind_port = int(os.getenv('PORT', DEFAULT_PORT))
bind_pair = (bind_ip, bind_port)

print('bind on %s:%d' % bind_pair)
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv_sock.bind(bind_pair)
serv_sock.listen(5)

while True:
    incoming_sock, addr = serv_sock.accept()

    print('connection from', addr)

    try:
        incoming_sock = ssl.wrap_socket(
                incoming_sock,
                keyfile='key/server.key',
                certfile='key/server.crt',
                server_side=True,
                ssl_version=ssl.PROTOCOL_TLSv1_2,
#                ciphers=(
#                    'ECDHE-RSA-AES256-GCM-SHA384', 'DHE-DSS-AES256-GCM-SHA384',
#                    'DHE-RSA-AES256-GCM-SHA384', 'DH-DSS-AES256-GCM-SHA384'
#                    )
                )
    except:
        print('[server] can not wrap incoming socket')
        incoming_sock = None
        continue

    target_port = int(os.getenv('TARGET_PORT', DEFAULT_TARGET_PORT))
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_sock.connect(('127.0.0.1', target_port))
    try:
        auth_result = auth_routine(incoming_sock)
    except sockutils.ProtocolError:
        auth_result = False
    try:
        if auth_result:
            incoming_sock.sendall(b'1')
            sockutils.binding_socket_pipe(incoming_sock, local_sock)
        else:
            incoming_sock.sendall(b'0')
    except:
        print('[server] unknow error during send auth result and piping')
