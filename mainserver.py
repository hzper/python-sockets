# import socket
# import selectors
# import types

# HOST = '127.0.0.1'
# PORT = 65432

# sel = selectors.DefaultSelector()
# nb_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# nb_socket.bind((HOST,PORT))
# nb_socket.listen()

# print("Slušam na",(HOST,PORT))
# nb_socket.setblocking(False)
# sel.register(nb_socket,selectors.EVENT_READ,data=None)

# def accept_wrapper(sock):

#     conn,addr = sock.accept()
#     print("Prihvaćena konekcija od ",addr)
#     conn.setblocking(False)
#     data = types.SimpleNamespace(addr=addr,inb=b'',outb=b'')
#     events = selectors.EVENT_READ | selectors.EVENT_WRITE

#     sel.register(conn,events,data=data)

# def service_connection(key,mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024) # vraća primljene podatke
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print("Zatvaranje konekcije za ",data.addr)
#             sel.unregister(sock)
#             sock.close()

#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print("S KLIJENTA: ",repr(data.outb),'-----',data.addr)
#             sent = sock.send(data.outb) #vraća broj poslanih bajtova
#             data.outb = data.outb[sent:]

# while True:
#     events = sel.select(timeout=None)
#     for key, mask in events:
#         if key.data is None:
#             accept_wrapper(key.fileobj)
#         else:
#             service_connection(key,mask)
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
lista_konekcija = []

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print("Prihvaćena konekcija na: ", addr)
    
    lista_konekcija.append(addr)
    
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print("Zatvaram konekciju na: ", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Echoing", repr(data.outb), "to", data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

HOST = '127.0.0.1'
PORT = 65432

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print("Osluškujem na: ", (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
                print(lista_konekcija)
                
except KeyboardInterrupt:
    print("Prekinuto izvršavanje, izlazim.")
finally:
    sel.close()