from socket import *
from datetime import datetime

def clock_diff(clientSocket):
    try:
        clientSocket.send(b'What time is it?') #sending a request to the time server
        clientSocket.settimeout(3) #setting socket time out to manage errors
        serverTime = clientSocket.recv(2048).decode('utf-8') #receiving the local time of the server
        clientTime = datetime.now().strftime("%H:%M:%S.%f") #getting the local time of the client
        #calculating the time difference between client and server
        clockDiff = datetime.strptime(serverTime,"%H:%M:%S.%f")-datetime.strptime(clientTime,"%H:%M:%S.%f")
        clockDiff=abs(clockDiff) 
        print(f'Client time : {clientTime}')
        print(f'Server time : {serverTime}')
        print(f'Clock difference is : {clockDiff}') #displaying the time difference
            
    except TimeoutError: #catching a socket time out error
        print('Connection timed out')
    except Exception as e:  #catching unexpected errors and displaying them
        print('An unexpected error occurred')
        print(e)
    finally:
        clientSocket.close() #closing the client socket
    


def run_client():
    serverName = input("input the address of the server (press enter if your server is on the same machine): ")
    serverName = serverName if serverName !='' else 'localhost' #defaulting to localhost if the servername is empty
    print(f'server name / address : {serverName}')
    serverPort = 10001
    
    clientSocket = socket(AF_INET, SOCK_STREAM) #setting up the TCP client socket
    clientSocket.connect((serverName,serverPort)) #initialting the connection with the tcp server
    clock_diff(clientSocket)
    
    
if __name__ == "__main__":
    run_client()
