from socket import *
from datetime import datetime
from threading import Thread

def handle_client(listeningSocket):
    while True:
        #accepting connections to TCP
        clientSocket, address = listeningSocket.accept()
        print(f'Connected to client {address}')
        while True:
            #sending the local time of the TCP server to client
            try:
                received = clientSocket.recv(2048).decode('utf-8')
                if not received :
                    #closing the socket if the server doesn't receive a message
                    print("No message received, closing socket")
                    clientSocket.close()
                    break
                else:
                    print(received)
                    to_send = datetime.now().strftime("%H:%M:%S.%f")
                    clientSocket.sendall((f'{to_send}').encode('utf-8'))
            except Exception as e: 
                #catching unexpected errors to avoid the server stopping and closing the socket
                print("Unexpected error occured")
                print(f"Error: {e}")

def start_server():
	portNumber = 10002
	serverSocket = socket(AF_INET, SOCK_STREAM) #setting up the tcp socket for the server
	serverSocket.bind(('', portNumber)) 
	serverSocket.listen(5) #listening to tcp connections
	for i in range(2):
        #using a pool of 4 threads to allow simulanoeus connections to TCP server
		Thread(target=handle_client,args=(serverSocket,)).start() 
	print(f"Server listening on port {portNumber}...")
    

if __name__ == "__main__":
    start_server()