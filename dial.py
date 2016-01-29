#!/usr/bin/env python3
from multiprocessing import Process
import socket
import struct

MCAST_GRP = '239.255.255.250'
MCAST_PORT = 1900
HOST_IP = socket.gethostbyname(socket.getfqdn())
HOST_PORT = 52235
msearch_string = 'urn:dial-multiscreen-org:service:dial:1'
msearch_response = """HTTP/1.1 200 OK
LOCATION: http://{ip}:{port}/dd.xml
CACHE-CONTROL: max-age=1800
EXT:
BOOTID.UPNP.ORG: 1
SERVER: OS/version UPnP/1.1 product/version
ST: {msearch_string}""".format(**{'ip': HOST_IP, 'port': HOST_PORT, 'msearch_string': msearch_string})

def discovery():
    mcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mcast_socket.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    mcast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        msg, addr = mcast_socket.recvfrom(1024)
        msg = msg.decode('utf-8')
        #print(msg)
        for line in msg.splitlines():
            line = line.split(':', 1)
            if line[0] == 'ST':
                if line[1].strip() == msearch_string:
                    #print(addr)
                    mcast_socket.sendto(msearch_response.encode('utf-8'), addr)

        #print()

def rest():
    rest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rest_socket.bind((HOST_IP, HOST_PORT))
    rest_socket.listen(1)
    
    while True:
        connection, client_address = rest_socket.accept()
        msg = connection.recv(1024)
        msg = msg.decode('utf-8')
        print(msg)

if __name__ == '__main__':
    m = Process(target=discovery)
    m.start()
    r = Process(target=rest)
    r.start()
