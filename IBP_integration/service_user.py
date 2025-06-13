import sys
sys.path.append('')

import socket
import threading
import time
import json
from RpaTools import *

class CenterServer:
    MAX_NETWORK_CONNECTIONS = 5
    URL = "http://localhost:8080/tasklist"

    def __init__(self, host="0.0.0.0", port=55332):
        self.host = host
        self.port = port
        self.clients = {}
        self.work_items = {}
        self.superman_items = {"Approve application": "Bank_IBP"}
        self.web_thread = None
        self.web_lock = threading.Lock()
        self.driver = None

    # start server
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(self.MAX_NETWORK_CONNECTIONS)
        print(f"Server listening on {self.host}:{self.port}")

        self.web_thread = threading.Thread(target=self.web_control)
        self.web_thread.start()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")

            username = client_socket.recv(1024).decode().strip()
            self.clients[username] = client_socket
            print(f"Client {username} connected")

            threading.Thread(target=self.communicate_client, args=(username,)).start()

    # web control thread
    def web_control(self):
        print(f"Web control thread start!")
        self.driver = open_chrome_page(self.URL)
        self.driver.implicitly_wait(10)

        login(self.driver, "demo", "demo")
        self.driver.implicitly_wait(10)

        need_sleep = False
        while True:
            if need_sleep:
                time.sleep(60)
            else:
                time.sleep(2)
            
            need_sleep = True
            if validate_work_item(self.driver, self.work_items, self.superman_item):
                print(f"have work item -- {self.work_items}")

                # ui control lock
                with self.web_lock:
                    for key in self.work_items:
                        work_item_tuple = self.work_items[key]
                        if work_item_tuple[1] == 0:
                            span = work_item_tuple[0]
                            span.click()
                            print(f"click work item -- {key}")
                            time.sleep(1)

                            rpa_data = get_work_item_data_superman(self.driver, key)
                            print(f"get RPA data -- {key} -- data: {rpa_data}")
                            
                            self.send_work_item(rpa_data)
                            self.work_items[key] = (span, 1)
                    
                need_sleep = False
            else:
                print("no work item")

    def send_work_item(self, data):
        username = data["userName"]
        if username in self.clients:
            json_data = json.dumps(data)
            self.clients[username].sendall(json_data.encode("utf-8"))
            print(f"Sent task {data["taskName"]} to {username}")
        else:
            print("User RPA is not exist!")

    # net communicate thread
    def communicate_client(self, username):
        print(f"Communicate with {username} thread start!")
        client_socket = self.clients[username]
        while True:
            try:
                json_data = client_socket.recv(1024).decode("utf-8")
                data = json.loads(json_data)
                if data["state"] == "completed":
                    print(f"Task completion from {username}")
                    self.click_complete_button(data)
                else:
                    print(f"Received unknow message from {username}: {data}")
            except json.JSONDecodeError:
                continue
            except ConnectionResetError:
                print(f"Client {username} disconnected")
                del self.clients[username]
                break
            except Exception as e:
                print(f"Error communicating with {username}: {e}")
                break

    def click_complete_button(self, data):
        key = f"RPA_{data["userName"]}_{data["taskName"]}"
        if key not in self.work_items:
            return
        
        # ui control lock
        with self.web_lock:
            work_item_tuple = self.work_items[key]
            span = work_item_tuple[0]
            span.click()
            time.sleep(1)

            finish_work_item(self.driver)
        
        print(f"Finish work item -- {key}")
        del self.work_items[key]

if __name__ == "__main__":
    server = CenterServer()
    server.start_server()