import threading
import ast
from socket import *

# Data required for formatting based on protocols
FORMAT = 'utf-8'


clientSocket = socket(AF_INET, SOCK_STREAM) #TCP connection
clientSocket.connect(('127.0.0.1',13000)) #connect client to server

UDPconnected = False

userName =''

def recieveMsgs():
    global userName
    while True:
        try:
            message = clientSocket.recv(1024).decode(FORMAT) #while the client is recieving messages from the server

            if message == "UserName request": #if the server is requesting the client's name:
                userName = input('Enter a username:\n')
                clientSocket.send(userName.encode(FORMAT)) #Send the username
            elif message == "disconnect":#if the client has chosen to diconnect from the server
                 print("You have left the server.\n")
                 clientSocket.close()
                 break #end the loop
            elif  "Establishing connection..." in message: #server sends the client the other clients information so they can connect
                 
                 message = message.replace("Establishing connection...","")
                 theAnd = message.index("&")
                 ThisPeer = message[:theAnd] #convert string address back to tuple
                 OtherPeer = message[theAnd+1:]

                 ThisPeer = ast.literal_eval((message[:theAnd])) #convert string address back to tuple
                 OtherPeer = ast.literal_eval((message[theAnd+1:]))

                 peer_to_peer(ThisPeer, OtherPeer)

            else: 
                print(message) #if its not any of the specifc questions from the server then print the message

        except: #if the server stops running and the client stops recieving messages
                    
                    print("An error in the server has occured, you have been diconnected.\n")
                    clientSocket.close()
                    break
                    
            
def sendMsgs():
    global UDPconnected
    while True: 
            if UDPconnected == True: #while a peer-to-peer chatroom is running do not send messages to the server
                 continue
            else:
                message = input("")
                ##if message == '4': #if the client want to disconnect, print out that they have left the server and cloe the connection
                    #clientSocket.send(message.encode('utf-8'))
                    ##clientSocket.close()
                    #print("You have left the server")
                
                #else:
                clientSocket.send(message.encode(FORMAT)) #Send encoded message to another client

##### UDP P2P: #####

def peer_to_peer(ThisPeer, OtherPeer):
    global UDPconnected
    UDPconnected = True

    peerSocket = socket(AF_INET, SOCK_DGRAM) #create UDP connection
    peerSocket.bind(ThisPeer) #bind the socket to the raddr of this peer
    
    Thread_Recievep2p = threading.Thread(target= Recievep2p, args=(peerSocket,))
    Thread_Recievep2p.start()

    Thread_Sendp2p = threading.Thread(target= Sendp2p, args= (OtherPeer,peerSocket))
    Thread_Sendp2p.start()

    
    print("(You can type 'exit' to leave the chatroom).\n")
    print("connection established, press enter to start chat:\n")

def Recievep2p(peerSocket):
    global UDPconnected
    
    while True:
        try:
            receiveMsg, oPeer = peerSocket.recvfrom(1024)
            print(receiveMsg.decode(FORMAT))

            if ("has left the chatroom.\n") in receiveMsg.decode(FORMAT):
                clientSocket.send("exit".encode(FORMAT))  # Send the exit message
                UDPconnected = False
                break
        except:
             print("")
             UDPconnected = False
             break

    peerSocket.close()# Close the peer-to-peer socket
    return "" # Exit the function
        

def Sendp2p(OtherPeer,peerSocket):
    global userName
    global UDPconnected

    while True:
        try:
            message = userName + ": " + input(">> ")
            peerSocket.sendto(message.encode(FORMAT), OtherPeer)

            if "exit" in message.lower():
                message = userName + " has left the chatroom.\n"
                peerSocket.sendto(message.encode(FORMAT), OtherPeer) #tell the other peer the current peer has disconnected from the chatroom
                clientSocket.send("exit".encode(FORMAT))  # Send the exit message
                UDPconnected = False
                break
        except:
             print("")
             UDPconnected = False
             break
             
    peerSocket.close()# Close the peer-to-peer socket
    return ""  # Exit the function
    

####TCP CLIENT-SERVER THREADING####
recieveMsgs_Thread = threading.Thread(target= recieveMsgs)
recieveMsgs_Thread.start()

sendMsgs_Thread = threading.Thread(target= sendMsgs)
sendMsgs_Thread.start()

