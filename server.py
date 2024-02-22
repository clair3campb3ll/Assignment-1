import threading
from socket import *

host = '196.42.107.3'  #localhost #
serverPort = 13000  #port number

serverSocket = socket(AF_INET,SOCK_STREAM) #Indicate the server-client connection will be TCP

serverSocket.bind((host,serverPort)) #bind server port to localhost IP adress

serverSocket.listen() #Server starts listening for new connections

clients = [] #list of clients on the server
visibleClients = [] #list of visibly online clients' usernames
userNames = [] #Username of clients

def broadcastMessage(msg): #function to broadcast a message to all clients on the server
     for client in clients:
          client.send(msg)

def acceptClients(): #function to accept incoming client connections
    while True:
        print ("The server is listening...") #indicate the server is on

        connectionSocket, address = serverSocket.accept() #create a new socket called 'connectionSocket' with a dedicated connection between the client and the server

        thread = threading.Thread(target= handleClient, args=(connectionSocket,address)) #Each time a new client connection is accepted, a new thread to use the handleCLient function is started to handle clients simultaneously 
        thread.start()


def menuOptions(client): #function that sends the service options to the client and then provides a service based on the clients response
    option = ''
    while option != '4': #offer the menu options while the client is on the server

        client.send('\nSelect a Menue option:\n1.View online clients\n2.Chat to another client\n3.Settings\n4.Disconnect'.encode('utf-8'))
        option = client.recv(1024).decode('utf-8') #clients option

        if  str(option) == '1':
            client.send("Clients currently online:".encode('utf-8'))
            for visibleclient in visibleClients: #display in server all 'active server memebers'
                visibleclient = visibleclient+"\n"
                client.send(visibleclient.encode('utf-8')) #show the name that is at the same index number as the visbleclient #DOESN"T WORK
        elif str(option) == '2':
            client.send("service coming soon".encode('utf-8'))
            #Ask who the client would like to message and take there answer
            #Tell the client that the other client is not online or tell them there chat invitation has been sent
            #other client excepts the invite (in client.py)
            #udp connection established in client.py
        elif str(option) == '3':
            client.send("service coming soon".encode('utf-8'))
        elif str(option) == '4':
            client.close() #close connection
        else:
            client.send("service not avaliable".encode('utf-8'))


def handleClient(connectionSocket, address): #handle the clients' connections to the server and proved services
    while True:
        try:
            
            connectionSocket.send('UserName request'.encode('utf-8')) #ask client for its username
            userName = connectionSocket.recv(1024).decode('utf-8') #receive username from client

            userNames.append(userName) #add client's username to the list of users
            clients.append(connectionSocket) #add client to clients list

            print(f'{address}, aka {userName} has connected!') #indicate the client is connected to the server

            connectionSocket.send("You are now connected.".encode('utf-8')) #The connectionSocket tells the client they are connected to the server

            connectionSocket.send("Would you like to be visible to other members of the server?\ntype 'Yes' or 'No'".encode('utf-8')) #The connectionSocket asks if the client wants to be visible to other clients
            if connectionSocket.recv(1024).decode('utf-8').lower() == 'yes':
                visibleClients.append(userName)# add client to the list of 'active members of the server'
                broadcastMessage(f'{userName} has joined the server.'.encode('utf-8')) #tell all other clients on the server that a new client has joined
                connectionSocket.send('You are now visible to other server members.'.encode('utf-8'))

            else:
                connectionSocket.send('You are now invisible to other server members.'.encode('utf-8'))
        
        
            menuOptions(connectionSocket)
            
        except:  #if the client leaves the server:

            if connectionSocket in visibleClients: #if the client is visible to everyone else
                broadcastMessage(f'{connectionSocket}, aka {userName} left the server'.encode('utf-8'))
                print(f'{connectionSocket}, aka {userName} left the server'.encode('utf-8'))
            else:
                f'{connectionSocket}, aka {userName} left the server'.encode('utf-8')
            index = clients.index(connectionSocket)
            clients.remove(connectionSocket)
            connectionSocket.close()

            userName = userNames[index]
            userNames.remove(userName)
            for visibleclient in visibleClients:
                if userName in visibleClients:
                    visibleClients.remove(userName)
            


if __name__ == "__main__":
    print("The server is activated...")
    acceptClients()