import threading
from socket import * 

MSGFORMAT = 'utf-8'
ERRMSG = 'An unexpected error has occurred. '
ERRMSG1 = 'Unable to broadcast to clients. '
ERRMSG2 = 'Unable to connect to the client. '
ERRMSG3 = 'Unable to edit your status on the network. '


host = "127.0.0.1"#host's IP adress 
serverPort = 13000  #port number

serverSocket = socket(AF_INET,SOCK_STREAM) #Indicate the server-client connection will be TCP
serverSocket.bind((host,serverPort)) #bind server port to localhost IP adress
serverSocket.listen() #Server starts listening for new connections

clientDictionary = {} #dictionary of key as the clients and the values as their usernames
clientSockets = [] #list of all the connection sockets of all the clients connected #CLEAR
clientPasswords = {} #CODE*****
clientStatusDictionary = {} #dictionary of client's usernames and whether they're online or offline

def broadcastMessage(msg): #function to broadcast a message to all clients on the server
     for socket in clientSockets:
        try:
            socket.send(msg)
        except:
            print(ERRMSG1)


def acceptClients(): #function to accept incoming client connections
    while True:
            print ("The server is listening... ") # indicate the server is on
            connectionSocket, address = serverSocket.accept() #create a new socket called 'connectionSocket' with a dedicated connection between the client and the server
            thread = threading.Thread(target= handleClient, args=(connectionSocket,address)) #Each time a new client connection is accepted, a new thread to use the handleCLient function is started to handle clients simultaneously 
            thread.start()

def p2pChat(connectionSocket, userName, address):

    connectionSocket.send("Who would you like to chat with? ".encode(MSGFORMAT)) #ask who the client wants to chat with
    for client in clientStatusDictionary.keys(): #display in server all 'online' server memebers
        if (clientStatusDictionary.get(client) == "online") and (client != userName) : #if the users on the server are 'online' and not the current user themself
            client = client+'\n'
            try:
                connectionSocket.send(client.encode(MSGFORMAT)) #show the name that is at the same index number as the visbleclient
            except:
                print(ERRMSG2)

    otherClient = connectionSocket.recv(1024).decode(MSGFORMAT) #username of the other client the client want to talk to
            
    while otherClient not in clientDictionary.values() : # while the other client isn't a username in the clientDictionary
        try:
            connectionSocket.send("That user doesn't seem to be avaliable.\n".encode(MSGFORMAT)) #ask who the client wants to chat with
            connectionSocket.send("Who would you like to chat with?\n".encode(MSGFORMAT)) #ask who the client wants to chat with
            for client in clientStatusDictionary.keys(): #display in server all 'online' server memebers
                if (clientStatusDictionary.get(client) == "online") and (client != userName) : #if the users on the server are 'online' and not the current user themself
                    client = client+'\n'
                    connectionSocket.send(client.encode(MSGFORMAT)) #show the name that is at the same index number as the visible client

            otherClient = connectionSocket.recv(1024).decode(MSGFORMAT) #username of the other client the client want to talk to
        except:
            print(ERRMSG2)
    for otherclientAdr in clientDictionary.keys(): #look for the other client's info in clientDictionary
        if otherClient == clientDictionary.get(otherclientAdr): #if the otherClient's username is in the clientDictionery
            print(f"{userName} and {otherClient} currently chatting. ")
            message = "<1><ESTCONN>"+"Establishing connection..."+str(address)+"&"+str(otherclientAdr) #send the current client and other clients address tuples as strings
            connectionSocket.send(message.encode(MSGFORMAT)) #ask who the client wants to chat with
    
    while connectionSocket.recv(1024).decode(MSGFORMAT) != "exit": #stay here while the clients are in the chat room and someone types 'exit'
        continue
    print((f"{userName} and {otherClient} have stopped chatting. "))

                        

def changeStatus(connectionSocket, userName):
    while len(clientDictionary) > 0: #while there are client's on the server
        connectionSocket.send('\nSelect a Menu option:\n1. Current status\n2. Change status\n3. Back '.encode(MSGFORMAT))
        option = connectionSocket.recv(1024).decode(MSGFORMAT) #clients option

        if str(option) == '1':
            if userName in clientStatusDictionary.keys():
                connectionSocket.send("You are currently 'Online'. ".encode(MSGFORMAT))

        elif str(option) == '2':
            while len(clientDictionary) > 0:
                try:
                    connectionSocket.send("\nSelect a Menu option:\n1. 'Online'\n2. 'Offline'\n3. Back ".encode(MSGFORMAT))
                    option = connectionSocket.recv(1024).decode(MSGFORMAT) #clients option

                    if str(option) == '1':
                        connectionSocket.send("You now appear as online and are visible to other members on the server.\n".encode(MSGFORMAT))
                        clientStatusDictionary.update({userName: "online"})
                        broadcastMessage(f'{userName} has joined the server.\n'.encode(MSGFORMAT))

                    elif str(option) == '2':
                        connectionSocket.send("You are now offline and are invisible to other members on the server.\n".encode(MSGFORMAT))
                        clientStatusDictionary.update({userName: "offline"})

                    elif str(option) == '3':
                        break #break loop and go back to previous menu options
                except:
                    print(ERRMSG3)  
        elif option == '3':
            break #break loop and go back to previous menu options
        else:
            connectionSocket.send("Service not available. ".encode(MSGFORMAT))



def menuOptions(connectionSocket, userName, address): #function that sends the service options to the client and then provides a service based on the clients response
    option = ''
    while len(clientDictionary) > 0: #offer the menu options while there are clients on the server
        try:
            connectionSocket.send('\nSelect a Menu option:\n1. View online clients\n2. Chat to another client\n3. Settings\n4. Disconnect '.encode(MSGFORMAT))
            option = connectionSocket.recv(1024).decode(MSGFORMAT) #clients option

            if  str(option) == '1':
                connectionSocket.send("Clients currently online: ".encode(MSGFORMAT))

                for client in clientStatusDictionary.keys(): #display in server all 'online' server memebers
                    if clientStatusDictionary.get(client) == "online":
                        client = client+'\n'
                        connectionSocket.send(client.encode(MSGFORMAT)) #show the name that is at the same index number as the visbleclient
            elif str(option) == '2':
                count = 0
                for status in clientStatusDictionary.values():#if no one is online except the current client is online
                    if status == "online":
                        count += 1
                if count < 2 and clientStatusDictionary.get(userName) == "online":
                    connectionSocket.send("No other server members online. ".encode(MSGFORMAT))
                else:
                    p2pChat(connectionSocket, userName, address) #execute the p2pChat function
            elif str(option) == '3':
                changeStatus(connectionSocket, userName)

            elif str(option) == '4': #close server-client relationship 
                connectionSocket.send("<1><EXTCLNT>".encode(MSGFORMAT))
                if clientStatusDictionary.get(userName) == "online": #if the client is 'online' to everyone else
                    broadcastMessage(f'{userName} has left the server. '.encode(MSGFORMAT)) #tell all other clients the client has left
                
                print(f'{address}, ({userName}) has left the server. ')
                connectionSocket.close()#close the connection
                del clientStatusDictionary[userName]#remove client from the clientStatusDictionary list
                del clientDictionary[address]#remove client's raddress from the clients list
                clientSockets.remove(connectionSocket)
                
            else:
                connectionSocket.send("Service not available. ".encode(MSGFORMAT))

        except:
            break

def handleClient(connectionSocket, address): #handle the clients' connections to the server and proved services
    userName = '' #initialise userName variable
    #while True: #loop function while the client is still on the server
    try:
        connectionSocket.send('<2><USERREQ>'.encode(MSGFORMAT)) #ask client for its username
        userName = connectionSocket.recv(1024).decode(MSGFORMAT) #receive username from client

        while userName in clientDictionary.values():#if the choosen username has been taken
            connectionSocket.send('That username is taken, please pick another: '.encode(MSGFORMAT)) #ask client for its username
            userName = connectionSocket.recv(1024).decode(MSGFORMAT) #receive username from client
            if userName not in clientDictionary.values(): #if the client has given a unqiue username then continue 
                break

        clientDictionary.update({address: userName})#add client's raddres and username to the dictionary of clients #connectionSocket instead of address
        clientSockets.append(connectionSocket)#list of all the client's sockets to be able to broadcast to them

        print(f'{address}, aka {userName} has connected. ') #indicate the client is connected to the server

        connectionSocket.send("You are now connected! ".encode(MSGFORMAT)) #The connectionSocket tells the client they are connected to the server

        connectionSocket.send("Would you like to be visible to other members of the server?\nType 'Yes' or 'No'. ".encode(MSGFORMAT)) #The connectionSocket asks if the client wants to be visible to other clients
        if connectionSocket.recv(1024).decode(MSGFORMAT).lower() == 'yes':
            clientStatusDictionary.update({userName : "online"})# add client to the list of 'active members of the server'
            broadcastMessage(f'{userName} has joined the server. '.encode(MSGFORMAT)) #tell all other clients on the server that a new client has joined
            connectionSocket.send("You now appear as 'Online' to other server members. ".encode(MSGFORMAT))

        else:
            clientStatusDictionary.update({userName: "offline"})
            connectionSocket.send("You now appear as 'Offline' to other server members. ".encode(MSGFORMAT))
        
        if len(clientDictionary) >0:
            try:
                menuOptions(connectionSocket,userName, address) #display the service menu options
            except:
                print("No clients are currently online. ")

            
    except:  #if the client leaves the server:
        for client in clientDictionary.keys(): #display in server all 'online' server memebers
            if clientDictionary.get(client) == userName:
                print(f"{client}, ({userName}) has left the server. ") #for testing purposes, change later

        if clientStatusDictionary.get(userName) == "online": #ERRORS?
            broadcastMessage(f"{userName} has left the server. ".encode(MSGFORMAT))
            
        connectionSocket.close()

        if address in clientDictionary:
            del clientDictionary[address] 
            del clientStatusDictionary[userName]
            clientSockets.remove(connectionSocket)
                #break


if __name__ == "__main__":
    print("The server is activated... ")
    acceptClients()

    
