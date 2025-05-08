from socket import *
from threading import *
import logging

banned_pages = ['/bannedpage']

# Configure censor for banned requests
banned_logger = logging.getLogger('banned_logger')
banned_logger.setLevel(logging.INFO)
banned_handler = logging.FileHandler('banned_requests.log')  # Log file for banned pages
banned_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
banned_logger.addHandler(banned_handler)


def log_banned_request(client_ip, uri):
    """Log the client's IP address and banned URI to the banned requests log."""
    log_message = f"Client {client_ip} requested BANNED URI {uri}"
    banned_logger.info(log_message)

def handle_client(listeningSocket):
    while True:
        clientSocket, client_addr = listeningSocket.accept()
        print(f'Connected to client {client_addr}')
        while True:
            try:
                clientSocket.settimeout(1)
                request = clientSocket.recv(4096)
                if not request.decode('utf-8') :
                    #if no message is received, the socket is closed
                    print('No message received, Socket closed')
                    clientSocket.close()
                    break
                else:
                    request = request.decode('utf-8')
                    # splitting the request which contains source IP in the prefix
                    request_addr, request_client = request.split(' ', 1)
                    print(f'Request from address : {request_addr}')
                    print(f'HTTP request from client received : {request_client}')
                    # Parsing URI from HTTP Get request
                    uri = request_client.splitlines()[0].split(" ")[1]
                    uri = uri[:-5] if uri.endswith('.html') else uri # Removing .html from URIs if necessary
                    # Checking if the requested page is banned
                    if uri in banned_pages:
                        # Sending a 403 Forbidden message which will indicate that access to URI requested
                        # is forbidden
                        HTTP_response ="HTTP/1.1 403 Forbidden\r\n\r\n"
                        print('logging banned request...') 
                        log_banned_request(request_addr,uri)
                        clientSocket.sendall(HTTP_response.encode('utf-8'))
                    else:
                        #if page is not forbidden, the request is relayed to the HTTP server
                        message_server = fetch_from_server(request_client.encode('utf-8'))
                        print(f'Relaying server response to client ...')
                        clientSocket.send(message_server)
                    print('-----------------------------------------------')
            except TimeoutError:
                clientSocket.close()
                print('Connection timed out')
                break
            except Exception as e:
                print(f'Unexpected error (client side) occured, Error : {e}')

def fetch_from_server(message):
    relaySocket = socket (AF_INET, SOCK_STREAM)
    relaySocket.connect(('localhost',20004))
    try:
        print('Fetching response from the server ...')
        relaySocket.send(message)
        message_received = relaySocket.recv(4096)
        if not message_received.decode('utf-8'):
            # If no message is received, the socket is closed
            print('No message received, Socket closed')
            relaySocket.close()
        else:
            print('Response from server received')
            return message_received
    except Exception as e:
        print(f'Unexpected error (server side) occured, Error : {e}')

def start_censor_relay():
    relayPort = 20003
    relaySocket = socket(AF_INET, SOCK_STREAM)
    relaySocket.bind(('', relayPort))
    relaySocket.listen(5)
    for i in range(1):
        Thread(target=handle_client, args=(relaySocket,)).start()
    print(f'Relay listening on port {relayPort}')

if __name__ == '__main__':
    start_censor_relay()