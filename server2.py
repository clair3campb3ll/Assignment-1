from socket import *
import threading
import queue

messages = queue.Queue()
clients = []

server = socket(AF_INET,SOCK_DGRAM) # UDP socket
server.bind(("127.0.0.1", 9999)) # bind to local port 9999

def receive(): 
    # receive function constantly gets messages from server and stores in a queue data structure compatible with threading
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass

def broadcast():
    # broadcast function constantly takes messages from queue which either adds a new client or broadcasts message
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP-TAG:"):
                        server.sendto(f"{name} joined!".encode(), client)
                    else:
                        server.sendto(message, client)
                except:
                    clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)