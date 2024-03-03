import threading
from socket import *

host = "196.42.107.3"#host's IP adress 
serverPort = 13002  #port number

serverSocket = socket(AF_INET,SOCK_STREAM) #Indicate the server-client connection will be TCP
serverSocket.bind((host,serverPort)) #bind server port to localhost IP adress
serverSocket.listen() #Server starts listening for new connections

clientDictionary = {} #dictionary of key as the clients and the values as their usernames
clientStatusDictionary = {} #dictionary of client's usernames and whether they're online or offline

def broadcastMessage(msg): #function to broadcast a message to all clients on the server
     for client in clientDictionary:
          client.send(msg)


def acceptClients(): #function to accept incoming client connections
    while True:
        
        print ("The server is listening...")#indicate the server is on
        connectionSocket, address = serverSocket.accept() #create a new socket called 'connectionSocket' with a dedicated connection between the client and the server

        thread = threading.Thread(target= handleClient, args=(connectionSocket,address)) #Each time a new client connection is accepted, a new thread to use the handleCLient function is started to handle clients simultaneously 
        thread.start()

        
def changeStatus(client, userName):
    while len(clientDictionary) > 0: #while there are client's on the server
                client.send('\nSelect a Menu option:\n1.Current status\n2.Change status\n3.Back'.encode('utf-8'))
                option = client.recv(1024).decode('utf-8') #clients option

                if str(option) == '1':
                    if userName in clientStatusDictionary.keys():
                        client.send("You are currently 'Online'".encode('utf-8'))

                elif str(option) == '2':
                    while len(clientDictionary) > 0:
                        client.send("\nSelect a Menu option:\n1.'Online'\n2.'Offline'\n3.Back".encode('utf-8'))
                        option = client.recv(1024).decode('utf-8') #clients option

                        if str(option) == '1':
                            client.send("You are now appear online and are visible to other members on the server".encode('utf-8'))
                            clientStatusDictionary.update({userName: "online"})
                            broadcastMessage(f'{userName} has joined the server'.encode('utf-8'))

                        elif str(option) == '2':
                            client.send("You are now offline and are invisible to other members on the server".encode('utf-8'))
                            clientStatusDictionary.update({userName: "offline"})

                        elif str(option) == '3':
                            break #break loop and go back to previous menu options

                elif option == '3':
                    break #break loop and go back to previous menu options
                else:
                    client.send("service not avaliable".encode('utf-8'))


def menuOptions(client, userName): #function that sends the service options to the client and then provides a service based on the clients response
    option = ''
    while len(clientDictionary) > 0: #offer the menu options while there are clients on the server

        client.send('\nSelect a Menu option:\n1.View online clients\n2.Chat to another client\n3.Settings\n4.Disconnect'.encode('utf-8'))
        option = client.recv(1024).decode('utf-8') #clients option

        if  str(option) == '1':
            client.send("Clients currently online:".encode('utf-8'))

            for user in clientStatusDictionary.keys(): #display in server all 'online' server memebers
                if clientStatusDictionary.get(user) == "online":
                    user = user+'\n'
                    client.send(user.encode('utf-8')) #show the name that is at the same index number as the visbleclient

        elif str(option) == '2':
            while client.recv(1024).decode('utf-8') != "Chat done." :#while a client hasn't ended the chatroom

                client.send("Who would you like to chat with?".encode('utf-8')) #ask who the client wants to chat with
                for user in clientStatusDictionary: #display in server all 'online' server memebers
                    if (clientStatusDictionary.get(user) == "online") and (user != userName) : #if the users on the server are 'online' and not the current user themself
                        user = user+'\n'
                        client.send(user.encode('utf-8')) #show the name that is at the same index number as the visbleclient

                otherClient = client.recv(1024).decode('utf-8') 
                if otherClient in clientStatusDictionary.keys():
                    client.send("Establishing connection...".encode('utf-8')) #ask who the client wants to chat with

        elif str(option) == '3':
            changeStatus(client, userName)

        elif str(option) == '4': #close server-client relationship 
            client.close()#close the connection
            if clientStatusDictionary.get(userName) == "online": #if the client is 'online' to everyone else
                broadcastMessage(f'{userName} left the server'.encode('utf-8')) #tell all other clients the client has left
                    
            del clientStatusDictionary[user]#remove client from the clientStatusDictionary list
            del clientDictionary[client]#remove client from the clients list
            
        else:
            client.send("service not avaliable".encode('utf-8'))



def handleClient(connectionSocket, address): #handle the clients' connections to the server and proved services
    while True: #loop function while the client is still on the server
        try:
            connectionSocket.send('UserName request'.encode('utf-8')) #ask client for its username
            userName = connectionSocket.recv(1024).decode('utf-8') #receive username from client

            while userName in clientDictionary.values():#if the choosen username has been taken
                connectionSocket.send('That username is taken, please pick another:'.encode('utf-8')) #ask client for its username
                userName = connectionSocket.recv(1024).decode('utf-8') #receive username from client
                if userName not in clientDictionary.values(): #if the client has given a unqiue username then continue 
                    break

            clientDictionary.update({connectionSocket: userName})#add client's ip and username to the dictionary of clients

            print(f'{address}, aka {userName} has connected') #indicate the client is connected to the server

            connectionSocket.send("You are now connected!".encode('utf-8')) #The connectionSocket tells the client they are connected to the server

            connectionSocket.send("Would you like to be visible to other members of the server?\ntype 'Yes' or 'No'".encode('utf-8')) #The connectionSocket asks if the client wants to be visible to other clients
            if connectionSocket.recv(1024).decode('utf-8').lower() == 'yes':
                clientStatusDictionary.update({userName : "online"})# add client to the list of 'active members of the server'
                broadcastMessage(f'{userName} has joined the server'.encode('utf-8')) #tell all other clients on the server that a new client has joined
                connectionSocket.send("You are now appear as 'Online' to other server members".encode('utf-8'))

            else:
                clientStatusDictionary.update({userName: "offline"})
                connectionSocket.send("You are now appear as 'Offline' to other server members".encode('utf-8'))
        
        
            menuOptions(connectionSocket,userName) #display the service menu options

            
        except:  #if the client leaves the server:
            print(f"{connectionSocket} ({userName}) has left the server") #for testing purposes, change later
            connectionSocket.close()
            del clientDictionary[connectionSocket]
            del clientStatusDictionary[userName]
            break


if __name__ == "__main__":
    print("The server is activated...")
    acceptClients()
