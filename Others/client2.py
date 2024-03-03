from socket import *
import threading
import random

client = socket(AF_INET,SOCK_DGRAM)
client.bind(("127.0.0.1",8999))

name = input("Nickname: ")

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except:
            pass

t = threading.Thread(target=receive)
t.start

client.sendto(f"SIGNUP_TAG:{name}".encode(), ("127.0.0.1", 9999))

while True:
    message = input("")
    if message == "!q":
        exit()
    else:
        client.sendto(f"{name}: {message}".encode(), ("127.0.0.1", 9999))
