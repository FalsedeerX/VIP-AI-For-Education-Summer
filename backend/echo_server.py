## DESC: Echo Server for Mimicking AI Model Query
## Coded by Falsedeer (Yu-Kuang Chen)
## CopyRight (C) All Rights Reserved

import socket
import mods

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 6666))
server.listen(5)


while True:
    handler, address = server.accept()
    data = handler.recv(1024)
    phrase = mods.hexdump(data, 8)
    print("[#]Received connection from: {ip}".format(ip=address[0]))
    print("[#]Incoming from port: {port}".format(port=address[1]))
    print(" ")
    if len(data) == 0:
        print("---------------------------------------")
        continue
    else:
        pass
    print("[#]Received data dump:")
    print(" ")
    print(phrase)
    print(" ")
    print("[#]Resending received data to {ip}".format(ip=address[0]))
    handler.sendall(data)
    print("---------------------------------------")
    print(" ")
    handler.shutdown(socket.SHUT_RDWR)
    handler.close()
