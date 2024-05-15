import socket
import json

class Client:
    def __init__(self, addr: str = "127.0.0.1", port: int = 65431) -> None:
        self.addr = addr
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
