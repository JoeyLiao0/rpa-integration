import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from configLoader import config


class BpmApiClient(ABC):
    """BPM API客户端基类"""
    def __init__(self):
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        pass

    @abstractmethod
    def get_task_list(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_task_data(self, task_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def complete_task(self, task_id: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @abstractmethod
    def start_process(self, process_key: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        pass


class Camunda7ApiClient(BpmApiClient):
    """Camunda 7 API客户端"""
    def __init__(self):
        super().__init__()
        self.base_url = config.get_camunda7_url()
        self.username = config.get_camunda7_username()
        self.password = config.get_camunda7_password()
        self.session = requests.Session()
        self.authenticated = False
    def authenticate(self) -> bool:
        if not self.base_url or not self.username:
            return False

        self.session.auth = (self.username, config.get_camunda7_password())
        try:
            response = self.session.get(f"{self.base_url}/engine-rest/engine")
            self.authenticated = response.status_code == 200
            return self.authenticated
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_task_list(self) -> List[Dict[str, Any]]:
        if not self.authenticated:
            return []

        try:
            response = self.session.get(f"{self.base_url}/engine-rest/task")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Failed to get task list: {e}")
            return []

    def get_task_data(self, task_id: str) -> Dict[str, Any]:
        if not self.authenticated:
            return {}

        try:
            response = self.session.get(f"{self.base_url}/engine-rest/task/{task_id}")
            if response.status_code == 200:
                task_data = response.json()

                var_response = self.session.get(f"{self.base_url}/engine-rest/task/{task_id}/variables")
                if var_response.status_code == 200:
                    task_data['variables'] = var_response.json()

                return task_data
            return {}
        except Exception as e:
            print(f"Failed to get task data: {e}")
            return {}

    def complete_task(self, task_id: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated:
            return False

        try:
            payload = {}
            if variables:
                payload['variables'] = variables

            response = self.session.post(
                f"{self.base_url}/engine-rest/task/{task_id}/complete",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Failed to complete task: {e}")
            return False

    def start_process(self, process_key: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated:
            return False

        try:
            payload = {}
            if variables:
                payload['variables'] = variables

            response = self.session.post(
                f"{self.base_url}/engine-rest/process-definition/key/{process_key}/start",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to start process: {e}")
            return False


class Camunda8ApiClient(BpmApiClient):
    """Camunda 8 本地 C8Run 环境，基于 Cookie 的认证"""

    def __init__(self):
        self.tasklist_url = config.get_camunda8_base_url()
        self.username = config.get_camunda8_username()
        self.password = config.get_camunda8_password()
        self.session = requests.Session()
        self.authenticated = False

    def authenticate(self) -> bool:
        try:
            login_url = f"{self.tasklist_url}/api/login"
            params = {
                "username": self.username,
                "password": self.password
            }
            resp = self.session.post(login_url, params=params)
            if resp.status_code in [200, 204]:
                self.authenticated = True
                return True
            elif resp.status_code == 401:
                print("Login failed: 401 Unauthorized - 用户名或密码错误")
                self.authenticated = False
                return False
            else:
                print(f"Login failed: {resp.status_code} {resp.text}")
                self.authenticated = False
                return False
        except Exception as e:
            print(f"Login exception: {e}")
            self.authenticated = False
            return False

    def get_task_list(self) -> List[Dict[str, Any]]:
        if not self.authenticated and not self.authenticate():
            return []
        try:
            url = f"{self.tasklist_url}/v1/tasks/search"
            # POST 空json表示搜索所有task 已完成的任务也会继续调用rpa
            payload = {
                "state": "CREATED"
            }
            resp = self.session.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Get task list failed: {resp.status_code} {resp.text}")
                return []
        except Exception as e:
            print(f"Get task list exception: {e}")
            return []

    def get_task_data(self, task_id: str) -> Dict[str, Any]:
        if not self.authenticated and not self.authenticate():
            return {}
        try:
            url = f"{self.tasklist_url}/v1/tasks/{task_id}"
            resp = self.session.get(url)
            if resp.status_code != 200:
                print(f"Get task data failed: {resp.status_code} {resp.text}")
                return {}
            task_data = resp.json()

            var_url = f"{self.tasklist_url}/v1/tasks/{task_id}/variables"
            var_resp = self.session.get(var_url)
            if var_resp.status_code == 200:
                task_data["variables"] = var_resp.json()
            return task_data
        except Exception as e:
            print(f"Get task data exception: {e}")
            return {}

    def complete_task(self, task_id: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated and not self.authenticate():
            return False
        try:
            url = f"{self.tasklist_url}/v1/tasks/{task_id}/complete"
            payload = {"variables": variables} if variables else {}
            resp = self.session.patch(url, json=payload)
            if resp.status_code in [200, 204]:
                return True
            else:
                print(f"Complete task failed: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"Complete task exception: {e}")
            return False

    def start_process(self, process_key: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated and not self.authenticate():
            return False
        try:
            url = f"{self.tasklist_url}/v1/process-instances"
            payload = {
                "bpmnProcessId": process_key,
            }
            if variables:
                payload["variables"] = variables
            resp = self.session.post(url, json=payload)
            if resp.status_code in [200, 201]:
                return True
            else:
                print(f"Start process failed: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"Start process exception: {e}")
            return False


def create_bpm_client(platform: str = "camunda7") -> BpmApiClient:
    """创建BPM客户端"""
    if platform.lower() == "camunda8":
        return Camunda8ApiClient()
    else:
        return Camunda7ApiClient()