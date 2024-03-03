from socket import *
import threading
import ast

# Data required for formatting based on protocols
FORMAT = 'utf-8'
USERREQ = '<2><USERREQ>'
ESTABCONN = '<1><ESTCONN>'
CLOSECLIENT = '<1><EXTCLNT>'

client_socket = socket(AF_INET, SOCK_STREAM)  # TCP connection
client_socket.connect(('127.0.0.1', 13000))  # Client connection to server

UDP_con = False
user_name = ''

print("Welcome! Press enter to continue. ")

def send_msgs():
# Function to send messages to the server/peer
    global UDP_con
    while True:
        if UDP_con:  # If a p2p chatroom is running, no messages are sent to the server 
            continue
        else:
            msg = input("")
            client_socket.send(msg.encode(FORMAT))  # Send encoded message to another client

def receive_msgs():
# Function to receive messages from the server
    global user_name
    while True:
        try:
            msg = client_socket.recv(1024).decode(FORMAT)  # Decodes messages from the client to the server

            if msg.startswith(USERREQ):  # If there is a username request from the server
                user_name = input('Enter a username: ')
                client_socket.send(user_name.encode(FORMAT))  # Client sends their username
            elif msg.startswith(CLOSECLIENT):  # If the client would like to disconnect from the server
                print("You have left the server. ")
                client_socket.close()
                break  # Ends the loop once the client has left the server
            elif msg.startswith(ESTABCONN):  # Server sends the client the other clients' information so they can connect
                msg = msg[12:]

                msg = msg.replace("Establishing connection...", "")
                theAnd = msg.index("&")
                this_peer = ast.literal_eval((msg[:theAnd]))  # String address is converted to a tuple
                other_peer = ast.literal_eval((msg[theAnd + 1:]))

                peer_to_peer(this_peer, other_peer) # Calls the p2p function

            else:
                print(msg)  # If none of the above, the message is printed

        except:  # If an error occurs and the server and client cannot receive or send messages
            print("There has been an error which has occurred with the server, you are now disconnected from the server. ")
            client_socket.close() # Client is disconnected from the server
            break

def peer_to_peer(ThisPeer, other_peer):
# Function to enable p2p chatrooms using a UDP connection
    global UDP_con
    UDP_con = True

    peer_socket = socket(AF_INET, SOCK_DGRAM)  # UDP connection created
    peer_socket.bind(ThisPeer)  # Bind the socket to the peer's address

    # Creates threads for receiving and sending messages
    receivep2p_thread = threading.Thread(target= receive_p2p, args=(peer_socket,))
    sendp2p_thread = threading.Thread(target= send_p2p, args=(other_peer, peer_socket))

    # Creates threads receiving and sending messages
    receivep2p_thread.start() 
    sendp2p_thread.start() 

    print("Connection successfully established, press enter to begin chat: ")
    print("(You may type 'exit' to leave the chatroom. )")

def receive_p2p(peer_socket):
# Function for receiving p2p messages
    global UDP_con

    while True:
        try:
            receiveMsg, oPeer = peer_socket.recvfrom(1024)
            print(receiveMsg.decode(FORMAT))

            if "has left the chatroom." in receiveMsg.decode(FORMAT):
                client_socket.send("exit".encode(FORMAT))  # Exit message is sent if another peer has exited
                UDP_con = False
                break # Exits while loop and ends the chatroom
        except:
            UDP_con = False
            break

    peer_socket.close()  # P2p socket is closed
    return ""  # Exit out of the function

def send_p2p(other_Peer, peer_socket):
# Function for sending p2p messages
    global user_name
    global UDP_con

    while True:
        try:
            
            msg = user_name + ": " + input()
            peer_socket.sendto(msg.encode(FORMAT), other_Peer)

            if "exit" in msg.lower():
                msg = user_name + " has left the chatroom."
                peer_socket.sendto(msg.encode(FORMAT), other_Peer)  # The other peer is notified that the current peer has left the chatroom
                print("This chatroom has ended. ")
                client_socket.send("exit".encode(FORMAT))  # Exit message is sent
                UDP_con = False
                break
        except:
            UDP_con = False
            break

 
    peer_socket.close()  # Socket is closed
    return ""  # Exit out of the function


# Client-server TCP threading
# Start threads for receiving and sending messages
rec_msgs_thread = threading.Thread(target=receive_msgs)
send_msgs_thread = threading.Thread(target=send_msgs)

# Start threads for receiving and sending messages
rec_msgs_thread.start()
send_msgs_thread.start() 