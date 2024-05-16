"""Module containing the communication interfaces for the test stand and control system. Designed to work over a network connection using TCP sockets and python dicinaries serialized to JSON for transmission.
"""
import socket
import json
import sys
from typing import Any

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
        
        if port == 0:
            self.port = 65431
        else:
            self.port = port
        
        if "-v" in sys.argv:
            self.verbose = True
        else:
            self.verbose = False
        if "-debug" in sys.argv:
            self.debug = True
        else:
            self.debug = False
        return

    def sendData(self, sendData: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
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

        if port == 0:
            self.port = 65431
        else:
            self.port = port

        if "-v" in sys.argv:
            self.verbose = True
        else:
            self.verbose = False
        if "-debug" in sys.argv:
            self.debug = True
        else:
            self.debug = False
        return
    
    def recieveData(self, sendData: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.addr, self.port))
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                if self.verbose:
                    print(f"Connected by {addr}")
                recvData = conn.recv(20240)
                #print(f"Recieved {json.loads(recvData.decode())}")
                if not recvData:
                    print("No data recieved")
                    return dict()
                #print(f"sending {sendData} back to client")
                conn.sendall(json.dumps(sendData).encode())
                conn.close()
                return json.loads(recvData.decode())
