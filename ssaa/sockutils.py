import socket
import threading

class ProtocolError(ValueError):
    pass

def readint_from_socket(sock, byteorder='little'):
    data = sock.recv(4)
    if len(data) < 4:
        raise ProtocolError('malformd packet')
    return int.from_bytes(data, byteorder=byteorder)

def recvstring_from_socket(sock):
    length = readint_from_socket(sock)
    if length > 1024:
        raise ProtocolError('buffer too long')
    data = sock.recv(length)
    while len(data) < length:
        t = sock.recv(length - len(data))
        if not t:
            raise ProtocolError('malformd packet')
        data += t
    return data

def sendstring_to_socket(sock, data):
    sock.sendall(len(data).to_bytes(4, 'little'))
    sock.sendall(data)

# http://code.activestate.com/recipes/483730-port-forwarding/
def socket_pipe(src, dst):
    while True:
        buffer = src.recv(1024)
        if buffer:
            dst.sendall(buffer)
        else:
            try: src.shutdown(socket.SHUT_RD)
            except OSError: pass
            try: dst.shutdown(socket.SHUT_WR)
            except OSError: pass
            return

def binding_socket_pipe(p1, p2):
    threading.Thread(target=socket_pipe, args=(p1, p2)).start()
    threading.Thread(target=socket_pipe, args=(p2, p1)).start()
