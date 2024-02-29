from socket import *
import threading


def Send ():
    while True:
        socket.sendto(input(">>").encode('utf-8'),otherPeer)

def Recieve():
     while True:
        receiveMsg, oPeer = socket.recvfrom(1024)
        print(str(oPeer)+': '+receiveMsg.decode("utf-8"))

if __name__ == "__main__":
    thisPeer = (('127.0.0.1', 3000))

    socket = socket(AF_INET, SOCK_DGRAM)
    socket.bind(thisPeer)
    otherPeer=(('127.0.0.1', 3001))

    print("connection established")
    
    Thread_Recieve = threading.Thread(target= Recieve)
    Thread_Recieve.start()

    Thread_Send = threading.Thread(target= Send)
    Thread_Send.start()




