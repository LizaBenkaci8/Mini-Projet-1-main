from socket import *
from threading import *

cache = {}

def handle_client(listeningSocket):
    while True:
        clientSocket, client_addr = listeningSocket.accept()
        print(f'Connected to client {client_addr}')
        while True:
            try:
                clientSocket.settimeout(1)
                request_client = clientSocket.recv(4096)
                if not request_client.decode('utf-8'):
                    print('No message received, Socket closed')
                    clientSocket.close()
                    break
                else:
                    uri = request_client.decode('utf-8')
                    print('HTTP request from client received :')
                    print(uri.splitlines()[0])
                    uri = uri.splitlines()[0].split(" ")[1]
                    if uri in cache:
                        # sending a logging message to the logger relay
                        # logging message format : logging,client_ip,uri,response
                        logging_msg = f"logging,{client_addr[0]},{uri},{cache[uri]}"
                        fetch_from_server(logging_msg.encode('utf-8'))
                        # sending the cached response back to the client
                        print('Responding from cache...')
                        to_send = cache[uri]
                        to_send = to_send.encode('utf-8')
                        clientSocket.send(to_send)
                    else:
                        #prepending the address of the client to the request before sending
                        addr_request = f"{client_addr[0]} {request_client.decode('utf-8')}"
                        addr_request = addr_request.encode('utf-8')
                        message_server = fetch_from_server(addr_request)
                        if message_server.decode('utf-8').startswith('HTTP/1.1 403'):
                            #avoiding caching a banned page so that requests to banned pages can always be logged
                            print('Banned page, no caching')
                        else:
                            print('Adding response to cache')
                            cache[uri] = message_server.decode('utf-8')
                        print(f'Relaying server response to client ...')
                        clientSocket.send(message_server)
            except TimeoutError:
                print('Connection timed out')
                clientSocket.close()
                break
            except Exception as e:
                print(f'Unexpected error (client side) occured, Error : {e}')
            

def fetch_from_server(message):
    relaySocket = socket (AF_INET, SOCK_STREAM)
    relaySocket.connect(('localhost',20002))
    try:
        print('Page not found in cache, fetching response from the server ...')
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

def start_cache_relay():
    relayPort = 20001
    relaySocket = socket(AF_INET, SOCK_STREAM)
    relaySocket.bind(('', relayPort))
    relaySocket.listen(5)
    for i in range(1):
        Thread(target=handle_client, args=(relaySocket,)).start()
    print(f'Relay listening on port {relayPort}')

if __name__ == '__main__':
    start_cache_relay()