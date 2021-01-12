import socket
import selectors 
import types

messages = [b'Message 1 from client.', b'Message 2 from client.']

HOST = '127.0.0.1'
PORT = 65432
sel = selectors.DefaultSelector()
nb_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
nb_socket.bind((HOST,PORT))
nb_socket.listen()
print('Slušam na ', (HOST,PORT))
nb_socket.setblocking(False)
sel.register(nb_socket,selectors.EVENT_READ,data=None)


def start_connections (HOST,PORT,num_conns):
    server_addr = (HOST,PORT)
    for i in range (0,num_conns):
        connid = i + 1
        print("Spajanje ",connid," na ",server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        dataVAR = types.SimpleNamespace(connid=connid,
                msg_total = sum(len(m) for m in messages),
                recv_total = 0,
                messages = list(messages),
                outb=b'')

        sel.register(sock,events,data = dataVAR)

        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    pass
                else:
                    service_connection(key, mask)


def service_connection(key, mask):
        sock = key.fileobj
        dataSC = key.data
        if mask & selectors.EVENT_READ:
                recv_data = sock.recv(1024) # Should be ready to read
                if recv_data:
                        print('received', repr(recv_data), 'from connection',
                        dataSC.connid)
                        dataSC.recv_total += len(recv_data)
                if not recv_data or dataSC.recv_total == dataSC.msg_total:
                        print('closing connection', dataSC.connid)
                        sel.unregister(sock)
                        sock.close()

        if mask & selectors.EVENT_WRITE:
            if not dataSC.outb and dataSC.messages:
                dataSC.outb = dataSC.messages.pop(0)
        if dataSC.outb:
                print('sending', repr(dataSC.outb), 'to connection',
                dataSC.connid)
                sent = sock.send(dataSC.outb)
                dataSC.outb = dataSC.outb[sent:]