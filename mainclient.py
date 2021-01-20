# import socket
# import selectors 
# import types

# HOST = '127.0.0.1'
# PORT = 65432
# num_conns = 2
# messages = [b'Prva poruka s klijenta.', b'Druga poruka s klijenta.']

# sel = selectors.DefaultSelector()

# def start_connections(HOST,PORT,num_conns):

#     server_addr = (HOST,PORT)
    
#     for i in range (0,num_conns):
#         connid = i + 1
#         print("Spajanje",connid,". konekcije na ",server_addr)
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setblocking(False)
#         sock.connect_ex(server_addr)
#         events = selectors.EVENT_READ | selectors.EVENT_WRITE
#         dataVAR = types.SimpleNamespace(connid=connid,
#                 msg_total = sum(len(m) for m in messages),
#                 recv_total = 0,
#                 messages = list(messages),
#                 outb=b'')

#         sel.register(sock,events,data= dataVAR)

#     while True:
#         events = sel.select(timeout=None)
#         for key, mask in events:
#                 if key.data is None:
#                         pass
#                 else:
#                         service_connection(key,mask)

# def service_connection(key, mask):

#         sock = key.fileobj
#         dataSC = key.data

#         if mask & selectors.EVENT_READ:

#                 recv_data = sock.recv(1024)
#                 if recv_data:
#                         print('Primljeno', repr(recv_data), 'od konekcije',
#                         dataSC.connid)
#                         dataSC.recv_total += len(recv_data)

#                 if not recv_data or dataSC.recv_total == dataSC.msg_total:
#                         print('Zatvaranje konekcije ', dataSC.connid)
#                         sel.unregister(sock)
#                         sock.close()
                        
#         if mask & selectors.EVENT_WRITE:

#                 if not dataSC.outb and dataSC.messages:
#                         dataSC.outb = dataSC.messages.pop(0)  

#                 if dataSC.outb:
#                         print('Javljanje ', repr(dataSC.outb), 'na konekciju',
#                         dataSC.connid)
#                         sent = sock.send(dataSC.outb)
#                         dataSC.outb = dataSC.outb[sent:]
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections(host, port, num_conns,ispis):
    
    server_addr = (host, port)
    
    for i in range(0, num_conns):
        connid = i + 1
        print("Pokrećem konekciju ", connid, "na", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=list(messages),
            outb=b"",
        )   
        sel.register(sock, events, data=data)
        

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("Received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("Closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("Sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

HOST = '127.0.0.1'
PORT = 65432

if len(sys.argv) != 3:
    print("Pokreni na način: ", sys.argv[0], "<num_connections> <0 ili 1 ako želiš ispis>")
    sys.exit(1)

num_conns = sys.argv[1]
ispis = sys.argv[2]

start_connections(HOST,PORT, int(num_conns),int(ispis))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
                # pass
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
        
except KeyboardInterrupt:
    print("Prekinuto izvršavanje, izlazim.")
finally:
    sel.close()