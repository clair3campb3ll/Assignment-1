import threading
from socket import *

clientSocket = socket(AF_INET, SOCK_STREAM) #TCP connection
clientSocket.connect(('127.0.0.1',13000)) #connect client to server


Connected = True #if the client is connected to the server
userName =''


def recieveMsgs():
    global Connected, userName
    while True:
        try:
            message = clientSocket.recv(1024).decode('utf-8') #while the client is recieving messages from the server

            if message == "UserName request": #if the server is requesting the client's name:
                userName = input('Enter a username:\n')
                clientSocket.send(userName.encode('utf-8')) #Send the username

            elif "Establishing connection..." in message: #server sends the client the other clients information so they can connect
                 message = message.replace("Establishing connection...","")
                 OtherPeer = message 
                 print(OtherPeer)
                 print("TEST1")#DELETE
                 peer_to_peer(OtherPeer)
                 print("TEST2")#DELETE

            else: 
                print(message) #if its not any of the specifc questions from the server then print the message

        except: #if the server stops running and the client stops recieving messages
                if Connected == True: #if the client socket connection hasn't been closed already **doesn't work, boradcasts to every client
                    print("An error in the server has occured. You have been disconnected")
                    clientSocket.close()
                    Connected = False
                    break
                    
            

def sendMsgs():
    global Connected
    while True:
            message = input("")
            if message == '4': #if the client want to disconnect, print out that they have left the server and cloe the connection
                 clientSocket.send(message.encode('utf-8'))
                 clientSocket.close()
                 print("You have left the server")
                 Connected = False # client is no longer on the server
            
            else:
                clientSocket.send(message.encode('utf-8')) #Send encoded message to another client


def peer_to_peer(OtherPeer):
    print("TEST3")#DELETE
    peerSocket = socket(AF_INET, SOCK_DGRAM)
    ThisPeer = peerSocket.getpeername()
    peerSocket.bind(ThisPeer) #get the raddr of this peer
    
    
    print("connection established, you may start typing")
    print("You can type 'exit' to leave the chatroom")
    
    Thread_Recievep2p = threading.Thread(target= Recievep2p)
    Thread_Recievep2p.start()

    Thread_Sendp2p = threading.Thread(target= Sendp2p, args= (OtherPeer,peerSocket))
    Thread_Sendp2p.start()

def Sendp2p(OtherPeer,peerSocket):
    global userName

    while (message != ">>exit") or (message != ">>exit"):
        message = input(">>")
        socket.sendto(message.encode('utf-8'),OtherPeer)
    
    message = userName+" has left the chatroom" #GET USERNAME
    socket.sendto(message.encode('utf-8'),OtherPeer)
    
    peerSocket.close() ##CHECK
    clientSocket.send("exit".encode('utf-8')) #tell the server that the peer-to-peer chat is closed
    

def Recievep2p():
     while True:
        receiveMsg, OtherPeer = socket.recvfrom(1024)
        print(str(OtherPeer)+': '+receiveMsg.decode("utf-8"))

####TCP CLIENT-SERVER THREADING####
recieveMsgs_Thread = threading.Thread(target= recieveMsgs)
recieveMsgs_Thread.start()

sendMsgs_Thread = threading.Thread(target= sendMsgs)
sendMsgs_Thread.start()

