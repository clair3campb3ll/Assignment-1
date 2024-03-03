import threading
from socket import *

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(('127.0.0.1',13002)) #connect client to server

otherClientIP = '127.0.0.1'
otherClientPort = 4096 #port we are sending data to
clientPort = 4095

clientSocketp2p = socket(AF_INET, SOCK_DGRAM) #create a udp connection for the clients to communicate over
clientSocketp2p.bind(('127.0.0.1',clientPort)) #bind the client to its source port


Connected = True #if the client is connected to the server


def recieveMsgs():
    global Connected
    while True:
        try:
            message = clientSocket.recv(1024).decode('utf-8') #while the client is recieving messages from the server

            if message == "UserName request": #if the server is requesting the client's name:
                userName = input('Enter a username:')
                clientSocket.send(userName.encode('utf-8')) #Send the username

            elif message == "Establishing connection...": #server sends the client the other clients information so they can connect
                 #HOW TO GET USERNAME??
                 print("Test")
                 p2pChat(otherClientIP, otherClientPort)
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

def p2pChat(otherClientIP, otherClientPort):
     print("Test")
     clientSocketp2p.sendto(f"{clientSocket} wants to chat!".encode("utf-8"), (otherClientIP, otherClientPort))
     print('ready to exchange messages\n')

     p2pRecieveMsgs_Thread = threading.Thread(target=p2pRecieveMsgs)
     p2pRecieveMsgs_Thread.start()

     p2pSendMsgs_Thread = threading.Thread(target=p2pSendMsgs)
     p2pSendMsgs_Thread.start()

def p2pRecieveMsgs(): #recieve messages from the other client
    #clientSocketp2p = socket(AF_INET,SOCK_DGRAM)
    #clientSocketp2p.bind(('172.27.144.1', clientPort)) #bind clientSocketp2p to another source port
    while True:
        message, address = clientSocketp2p.recvfrom(1024)
        print(address+ ": "+message.decode('utf-8')) #otherClientIP
     
def p2pSendMsgs():
    #clientSocketp2p = socket(AF_INET, SOCK_DGRAM)
    #clientSocketp2p.bind(('172.27.144.1', otherClientPort)) #bind clientSocketp2p to the destination port

    while True:
        message = input('-> ')
        if message == "->exit": #if the client leave the chatroom
            clientSocketp2p.close() 
            clientSocketp2p.sendto("Chatroom has closed.".encode('utf-8'), (otherClientIP, otherClientPort))
            clientSocket.send("Chat done.".encode('utf-8'))
        else:
            clientSocketp2p.sendto(message.encode('utf-8'), (otherClientIP, otherClientPort))

####THREADING####
recieveMsgs_Thread = threading.Thread(target= recieveMsgs)
recieveMsgs_Thread.start()

sendMsgs_Thread = threading.Thread(target= sendMsgs)
sendMsgs_Thread.start()

