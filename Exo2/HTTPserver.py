from socket import *
from pathlib import Path
from threading import *

def handle_client(listeningSocket):
	#initializing the directory of the file containing the web pages
	webPages_dir = Path(__name__).parent / 'WebPages'
	while True:
		# Accept incoming client connection
		client_connection, client_address = listeningSocket.accept()
		print(f"Connected by {client_address}")
		while True:
			# Receive the HTTP request from the client
			print("-------------------------------------")
			try:
				client_connection.settimeout(1)
				request = client_connection.recv(4096).decode("utf-8")
				print("-------------------------------------")
				print(f"Request:\n{request}")
				if not request:
					# If no message received, the socket is closed
					print('No message received, Socket closed')
					client_connection.close()
					break
				else:
					# Extract the requested file from the HTTP GET request
					# Splitting the request line to get the file name (after GET )
					request_line = request.splitlines()[0]
					print(f"Request Line: {request_line}") #printing the GET request
					file_requested = request_line.split(" ")[1]
						
					if file_requested == "/":  # Default to index.html if no file specified
						file_requested = "index.html"
					#ajouter une ligne pour reconnaitre les pages demandees sans avoir a ajouter .html
					if not file_requested.endswith('.html'):
						file_requested+='.html'

					# Building the file path by combining the directory and the file requested
					file_path =  webPages_dir / file_requested.lstrip('/')
					# Check if the file exists
					if file_path.exists():
						# Open and read the HTML file
						with open(file_path, "r") as f:
							content = f.read()

						# Create HTTP response with status 200 OK
						http_response = "HTTP/1.1 200 OK\r\n"
						http_response += "Content-Type: text/html; charset=utf-8\r\n"
						http_response += "\r\n"
						http_response += f"{content}\r\n\r\n"
					else:
						# If the file doesn't exist, return 404 Not Found
						http_response = "HTTP/1.1 404 Not Found\r\n"
						http_response += "Content-Type: text/html; charset=utf-8\r\n"
						http_response += "\r\n"
						http_response += "<html><head><title>404 Not Found</title>\r\n"
						http_response += "</head><body><h1>404 Not Found</h1></body></html>\r\n\r\n"
			except TimeoutError:
				client_connection.close()
				print('Connection timed out')
				break
			except Exception as e:
				# responds to unexpected errors with a 500 Internal Server Error
				http_response = "HTTP/1.1 500 Internal Server Error\r\n"
				http_response += "Content-Type: text/html; charset=utf-8\r\n"
				http_response += "\r\n"
				http_response += "<html><head><title>500 Internal Server Error</title>\r\n"
				http_response += f"</head><body><h1>500 Internal Server Error</h1><p>{str(e)}</p></body></html>\r\n\r\n"
			
			# Send the response back to the client
			client_connection.sendall(http_response.encode("utf-8"))
	
def start_server():
    portNumber = 20004
    serverSocket = socket(AF_INET, SOCK_STREAM) #setting up the TCP socket for the server
    serverSocket.bind(('', portNumber)) #binding the server IPv4 addresses and the port for listening
    serverSocket.listen(5)
    print(f"Server listening on port {portNumber}...")
    for i in range(1):
		#setting a pool of 4 threads to manage simultaneous connections to the TCP server
    	Thread(target=handle_client,args=(serverSocket,)).start()

    

if __name__ == "__main__":
    start_server()
