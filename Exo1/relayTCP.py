from socket import *
from threading import *

def handle_client(listeningSocket):
    while True:
        clientSocket, client_addr = listeningSocket.accept() #accepting connection on relay socket.
        print(f'Connected to client {client_addr}') 
        while True:
            try: 
                message_client = clientSocket.recv(2048) 
                if not message_client :
                    #if no message is received, the socket is closed
                    print('No message received, closing socket')
                    clientSocket.close()
                    break
                else:
                    print('message from client received')
                    #fetching the server response
                    message_server= fetch_from_server(message_client)
                    print(f'Relaying server response to client ...')
                    clientSocket.send(message_server)
            except Exception as e:
                print(f'Unexpected error (client side) occured, Error : {e}')

def fetch_from_server(message):
    relaySocket = socket (AF_INET, SOCK_STREAM)
    relaySocket.connect(('localhost',10002)) #connecting the relay socket to the server socket. 
    try:
        print('Fetching response from the server ...')
        relaySocket.send(message)
        message_received = relaySocket.recv(2048)
        if not message_received.decode('utf-8'):
            print('No message received, Socket closed')
            relaySocket.close()
        else:
            print('Response from server received')
            return message_received
    except Exception as e:
        print(f'Unexpected error (server side) occured, Error : {e}')
    

def start_relay():
    relayPort = 10001
    relaySocket = socket(AF_INET, SOCK_STREAM)
    relaySocket.bind(('', relayPort))
    relaySocket.listen(5)
    for i in range(2): #setting a pool of threads. (depending on the server/ machine capacity)
        Thread(target=handle_client, args=(relaySocket,)).start()
    print(f'Relay listening on port {relayPort}')

if __name__ == '__main__':
    start_relay()