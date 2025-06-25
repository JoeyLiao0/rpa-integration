import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from configLoader import config


class BpmApiClient(ABC):
    """BPM API客户端基类"""
    def __init__(self):
        self.base_url = config.get_api_url()
        self.username = config.get_username()
        self.api_key = config.get_api_key()
        self.session = requests.Session()
        self.authenticated = False

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
    def authenticate(self) -> bool:
        if not self.base_url or not self.username:
            return False

        self.session.auth = (self.username, config.get_login_password())
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
    """Camunda 8 API客户端"""
    def __init__(self):
        super().__init__()
        self.oauth_token = None

    def authenticate(self) -> bool:
        if not self.base_url or not self.api_key:
            return False

        try:
            auth_url = f"{self.base_url}/oauth/token"
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.username,
                'client_secret': self.api_key
            }

            response = requests.post(auth_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                self.oauth_token = token_data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.oauth_token}',
                    'Content-Type': 'application/json'
                })
                self.authenticated = True
                return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_task_list(self) -> List[Dict[str, Any]]:
        if not self.authenticated:
            return []

        try:
            query = {
                "query": """
                query GetTasks {
                    tasks(query: {}) {
                        id
                        name
                        taskDefinitionId
                        processName
                        assignee
                        creationTime
                        variables {
                            name
                            value
                        }
                    }
                }
                """
            }

            response = self.session.post(f"{self.base_url}/v1/graphql", json=query)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('tasks', [])
            return []
        except Exception as e:
            print(f"Failed to get task list: {e}")
            return []

    def get_task_data(self, task_id: str) -> Dict[str, Any]:
        if not self.authenticated:
            return {}

        try:
            query = {
                "query": f"""
                query GetTask {{
                    task(id: "{task_id}") {{
                        id
                        name
                        taskDefinitionId
                        processName
                        assignee
                        creationTime
                        variables {{
                            name
                            value
                        }}
                    }}
                }}
                """
            }

            response = self.session.post(f"{self.base_url}/v1/graphql", json=query)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('task', {})
            return {}
        except Exception as e:
            print(f"Failed to get task data: {e}")
            return {}

    def complete_task(self, task_id: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated:
            return False

        try:
            payload = {'taskId': task_id}
            if variables:
                payload['variables'] = variables

            response = self.session.patch(f"{self.base_url}/v1/tasks/{task_id}/complete", json=payload)
            return response.status_code == 204
        except Exception as e:
            print(f"Failed to complete task: {e}")
            return False

    def start_process(self, process_key: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        if not self.authenticated:
            return False

        try:
            payload = {'bpmnProcessId': process_key}
            if variables:
                payload['variables'] = variables

            response = self.session.post(f"{self.base_url}/v1/process-instances", json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to start process: {e}")
            return False


def create_bpm_client(platform: str = "camunda7") -> BpmApiClient:
    """创建BPM客户端"""
    if platform.lower() == "camunda8":
        return Camunda8ApiClient()
    else:
        return Camunda7ApiClient()