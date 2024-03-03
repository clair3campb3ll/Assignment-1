from socket import *
import threading
import ast

# Data required for formatting based on protocols
FORMAT = 'utf-8'
USERREQ = '<2><USERREQ>'
ESTABCONN = '<1><ESTCONN>'
CLOSECLIENT = '<1><EXTCLNT>' 

clientSocket = socket(AF_INET, SOCK_STREAM) #TCP connection
clientSocket.connect(('127.0.0.1',13000)) #connect client to server

UDPconnected = False

userName =''

print("Welcome! Press enter to continue. ")

def recieveMsgs():
    global userName
    while True:
        try:
            msg = clientSocket.recv(1024).decode(FORMAT) #while the client is recieving messages from the server

            if msg[0:12] == USERREQ:  # if the server is requesting the client's name:
                userName = input('Enter a username:\n')
                clientSocket.send(userName.encode(FORMAT)) #Send the username
            elif msg[0:12]== CLOSECLIENT:    #  if the client has chosen to diconnect from the server
                 print("You have left the server. ")
                 clientSocket.close()
                 break  # end the loop
            elif ESTABCONN in msg[0:12]:   # server sends the client the other clients information so they can connect
                 msg = msg[12:]
                 
                 msg = msg.replace("Establishing connection...","")
                 theAnd = msg.index("&")
                 ThisPeer = msg[:theAnd]    # convert string address back to tuple
                 OtherPeer = msg[theAnd+1:]

                 ThisPeer = ast.literal_eval((msg[:theAnd]))    # convert string address back to tuple
                 OtherPeer = ast.literal_eval((msg[theAnd+1:]))

                 peer_to_peer(ThisPeer, OtherPeer)

            else: 
                print(msg)  # if its not any of the specific questions from the server then print the message

        except: #if the server stops running and the client stops recieving messages      
            print("An error in the server has occured, you have been diconnected. ")
            clientSocket.close()
            break
                               
def sendMsgs():
    global UDPconnected
    while True: 
            if UDPconnected == True: #while a peer-to-peer chatroom is running do not send messages to the server
                 continue
            else:
                msg = input("")
                clientSocket.send(msg.encode(FORMAT)) #Send encoded message to another client

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

    print("(You can type 'exit' to leave the chatroom). ")
    print("Connection established, press enter to start chat: \n")

def Recievep2p(peerSocket):
    global UDPconnected
    
    while True:
        try:
            receiveMsg, oPeer = peerSocket.recvfrom(1024)
            print(receiveMsg.decode(FORMAT))

            if ("has left the chatroom.") in receiveMsg.decode(FORMAT):
                clientSocket.send("exit".encode(FORMAT))  # Send the exit message
                UDPconnected = False
                break
        except:
             UDPconnected = False
             break

    peerSocket.close()# Close the peer-to-peer socket
    return "" # Exit the function
        
def Sendp2p(OtherPeer,peerSocket):
    global userName
    global UDPconnected

    while True:
        try:
            msg = userName + ": " + input(">> ")
            peerSocket.sendto(msg.encode(FORMAT), OtherPeer)

            if "exit" in msg.lower():
                msg = userName + " has left the chatroom."
                peerSocket.sendto(msg.encode(FORMAT), OtherPeer) #tell the other peer the current peer has disconnected from the chatroom
                clientSocket.send("exit".encode(FORMAT))  # Send the exit message
                UDPconnected = False
                break
        except:
             UDPconnected = False
             break
             
    peerSocket.close()# Close the peer-to-peer socket
    return ""  # Exit the function

####TCP CLIENT-SERVER THREADING####
recieveMsgs_Thread = threading.Thread(target= recieveMsgs)
recieveMsgs_Thread.start()

sendMsgs_Thread = threading.Thread(target= sendMsgs)
sendMsgs_Thread.start()

