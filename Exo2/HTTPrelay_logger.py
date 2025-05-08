from socket import *
from threading import *
import logging

# Configure logger for all requests
request_logger = logging.getLogger('request_logger')
request_logger.setLevel(logging.INFO)
request_handler = logging.FileHandler('requests.log')  # Log file for valid requests
request_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
request_logger.addHandler(request_handler)


def log_request(client_ip, uri, response):
    if not response:
        """Log the client's IP address and requested URI to the requests log."""
        log_message = f"Client {client_ip} requested URI {uri} and received an empty response"
    else:
        """Log the client's IP address and requested URI and the length of its response"""
        log_message = f"Client {client_ip} requested URI {uri} and received a response of {len(response.encode('utf-8'))} bytes"
    request_logger.info(log_message)

def handle_client(listeningSocket):
    while True:
        clientSocket, client_addr = listeningSocket.accept()
        print(f'Connected to client {client_addr}')
        while True:
            try:
                clientSocket.settimeout(1)
                request = clientSocket.recv(4096)
                if not request.decode('utf-8') :
                    # If no message received, the socket is closed
                    print('No message received, Socket closed')
                    clientSocket.close()
                    break
                else:
                    request = request.decode('utf-8')
                    if request.split(",")[0].startswith("logging"):
                        # If the message is a logging message, log it and close the socket
                        print('Logging request ...')
                        log_request(request.split(",")[1], request.split(",")[2],request.split(",")[3])
                        print('Closing socket ...')
                        clientSocket.close()
                        break
                    else:
                        # splitting the request which contains source IP in the prefix
                        request_addr, request_client = request.split(' ', 1)
                        print(f'Request from address : {request_addr}')
                        print(f'HTTP request from client received {request_client}')
                        # Parsing URI from HTTP Get request
                        uri = request_client.splitlines()[0].split(" ")[1]
                        uri = uri[:-5] if uri.endswith('.html') else uri # Removing .html from URIs if necessary

                        #sending the request with the source request ip address as prefix to the next relay
                        message_server = fetch_from_server(request.encode('utf-8'))
                        print(f'Relaying server response to client ...')
                        clientSocket.send(message_server)
                        response=message_server.decode('utf-8')
                        
                        print('Logging request ...')
                        log_request(request_addr,uri,response)
                print('-----------------------------------------------')
            except TimeoutError:
                print('Connection timed out')
                clientSocket.close()
                break
            except Exception as e:
                print(f'Unexpected error (client side) occured, Error : {e}')

def fetch_from_server(message):
    relaySocket = socket (AF_INET, SOCK_STREAM)
    relaySocket.connect(('localhost',20003)) # connecting to the next known relay (censor relay).
    """
    We can add an input method to always specify the address and port of the next relay or server.

    """
    try:
        print('Fetching response from the server ...')
        relaySocket.send(message)
        message_received = relaySocket.recv(4096)
        if not message_received.decode('utf-8'):
            print('No message received, Socket closed')
            relaySocket.close()
        else:
            print('Response from server received')
            return message_received
    except Exception as e:
        print(f'Unexpected error (server side) occured, Error : {e}')
    

def start_logger_relay():
    relayPort = 20002
    relaySocket = socket(AF_INET, SOCK_STREAM)
    relaySocket.bind(('', relayPort))
    relaySocket.listen(5)
    for i in range(1):
        Thread(target=handle_client, args=(relaySocket,)).start()
    print(f'Relay listening on port {relayPort}')

if __name__ == '__main__':
    start_logger_relay()