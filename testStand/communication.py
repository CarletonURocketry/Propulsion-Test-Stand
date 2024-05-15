"""Module containing the communication interfaces for the test stand and control system. Designed to work over a network connection using TCP sockets and python dicinaries serialized to JSON for transmission.
"""
import socket
import json

class Client:
    def __init__(self, addr: str = "127.0.0.1", port: int = 65431) -> None:
        """Class to interface with the server

        Args:
            addr (str, optional): IP address of the server. Defaults to "127.0.0.1".
            port (int, optional): Port to use for communication with the server. Defaults to 65431.
        """
        if addr == "":
            self.addr = "127.0.0.1"
        else:
            self.addr = addr
        
        if port == "":
            self.port = 65431
        else:
            self.port = port
        return

    def sendData(self, sendData: dict) -> dict:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.addr, self.port))
            #print(f"sending {sendData} to server")
            sock.sendall(json.dumps(sendData).encode())
            recvData = sock.recv(1024)
            recvData = json.loads(recvData.decode())
            #print(f"Recieved {recvData}")
        return recvData

class Server:
    def __init__(self, addr: str = "127.0.0.1", port: int = 65431):
        """Class to interface with the client

        Args:
            addr (str, optional): IP Address of the server. Defaults to "127.0.0.1".
            port (int, optional): Port to use for communication with the client. Defaults to 65431.
        """
        if addr == "":
            self.addr = "127.0.0.1"
        else:
            self.addr = addr

        if port == "":
            self.port = 65431
        else:
            self.port = port
        return
    
    def recieveData(self, sendData) -> dict:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.addr, self.port))
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    recvData = conn.recv(1024)
                    #print(f"Recieved {json.loads(recvData.decode())}")
                    if not recvData:
                        print("No data recieved")
                        break
                    #print(f"sending {sendData} back to client")
                    conn.sendall(json.dumps(sendData).encode())
                    return json.loads(recvData.decode())
