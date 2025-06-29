import sys

sys.path.append('')

import socket
import threading
import json
from RpaTools import *
from configLoader import config


class RpaClient:
    def __init__(self, username, server_host=None, server_port=None):
        self.server_host = server_host or config.get_server_host()
        self.server_port = server_port or config.get_server_port()
        self.username = username
        self.socket = None
        self.running = True

    def start_client(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"已连接到服务器 {self.server_host}:{self.server_port}")

            # 发送用户名
            self.socket.sendall(self.username.encode())
            print(f"已注册用户名: {self.username}")

            # 启动接收任务的线程
            receive_thread = threading.Thread(target=self.receive_tasks)
            receive_thread.daemon = True
            receive_thread.start()

            # 保持主线程运行
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("收到中断信号，正在关闭客户端...")
                self.stop_client()

        except Exception as e:
            print(f"启动客户端失败：{e}")

    def stop_client(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("客户端已关闭")

    def receive_tasks(self):
        while True:
            try:
                json_data = self.socket.recv(1024).decode("utf-8")
                data = json.loads(json_data)
                print(f"收到RPA任务数据: {data}")
                self.rpa_process_task(data)
            except json.JSONDecodeError:
                continue
            except ConnectionResetError:
                print("与服务器断开连接")
                break
            except Exception as e:
                print(f"接收任务时发生错误：{e}")
                break

    def rpa_process_task(self, data):
        username = data.get("userName", "")
        task_name = data.get("taskName", "")

        if username != self.username:
            return

        print(f"开始处理RPA任务：{task_name}")
        trigger_rpa(data)
        self.finish_rpa_task(data)

    def finish_rpa_task(self, data):
        data["state"] = "completed"
        json_data = json.dumps(data)
        self.socket.sendall(json_data.encode("utf-8"))
        print("已响应服务器：任务已完成")


if __name__ == "__main__":
    client = RpaClient("MACBOOK")
    client.start_client()
