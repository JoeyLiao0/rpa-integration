import sys
sys.path.append('')

import socket
import threading
import json
from RpaTools import *

class RpaClient:
    def __init__(self, username, server_host="127.0.0.1", server_port=55332):
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.socket = None
    
    def start_client(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

        self.socket.sendall(self.username.encode())
        threading.Thread(target=self.receive_tasks).start()

    def receive_tasks(self):
        while True:
            try:
                json_data = self.socket.recv(1024).decode("utf-8")
                data = json.loads(json_data)
                print(f"Get RPA data: {data}")
                self.rpa_process_task(data)
            except json.JSONDecodeError:
                continue
            except ConnectionResetError:
                print("Disconnected from server")
                break
            except Exception as e:
                print(f"Error receiving tasks: {e}")
                break
    
    def rpa_process_task(self, data):
        username = data["userName"]
        if username != self.username:
            return
        
        trigger_rpa(data)
        self.finish_rpa_task(data)

    def finish_rpa_task(self, data):
        data["state"] = "completed"
        json_data = json.dumps(data)
        self.socket.sendall(json_data.encode("utf-8"))
        print("Reponse server: task completed!")

if __name__ == "__main__":
    client = RpaClient("user1")
    client.start_client()
