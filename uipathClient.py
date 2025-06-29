# uipathClient.py
import threading
import time
import requests
import json
from configLoader import config


class UiPathOrchestrator:
    """UiPath Orchestrator 客户端"""

    def __init__(self):
        # 从配置加载 UiPath 设置
        self.organization = config.get_uipath_organization()
        self.tenant = config.get_uipath_tenant()
        self.pat = config.get_uipath_pat()
        self.folder_id = config.get_uipath_folder_id()
        self.robot_id = config.get_uipath_robot_id()

        # 构建基础 URL
        self.base_url = f"https://cloud.uipath.com/{self.organization}/{self.tenant}/orchestrator_"

        # 用于存储作业 Key 的临时缓存
        self.job_cache = {}
        self.cache_lock = threading.Lock()

        # 验证配置
        self.validate_config()


    def start_job(self, release_key, input_arguments=None):
        """启动 UiPath 作业"""
        start_job_endpoint = f"{self.base_url}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"

        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(self.folder_id)
        }

        json_input_arguments = None
        if input_arguments:
            try:
                json_input_arguments = json.dumps(input_arguments)
            except TypeError:
                print("[WARNING] 无法序列化输入参数，将使用 None")
                json_input_arguments = None

        payload = {
            "startInfo": {
                "ReleaseKey": release_key,
                "Strategy": "Specific",
                "RobotIds": [self.robot_id],
                "JobsCount": 0,
                "InputArguments": json_input_arguments
            }
        }

        try:
            response = requests.post(start_job_endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # 检查响应结构
            if "value" not in response.json() or not response.json()["value"]:
                raise ValueError("无效的 API 响应格式")

            job_key = response.json()["value"][0]["Key"]
            return job_key
        except requests.exceptions.RequestException as e:
            error_msg = f"启动作业失败: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" | 错误信息: {error_details.get('message', '未知错误')}"
                except:
                    error_msg += f" | 响应文本: {e.response.text[:200]}"
            raise Exception(error_msg)
        except (KeyError, IndexError, ValueError) as e:
            raise Exception(f"解析 API 响应失败: {str(e)}")

    def get_job_details(self, job_key):
        """获取作业详情"""
        get_job_endpoint = f"{self.base_url}/odata/Jobs({job_key})"

        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(self.folder_id)
        }

        try:
            response = requests.get(get_job_endpoint, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"获取作业详情失败: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" | 错误信息: {error_details.get('message', '未知错误')}"
                except:
                    error_msg += f" | 响应文本: {e.response.text[:200]}"
            raise Exception(error_msg)

    def cache_job_key(self, filename, job_key):
        """缓存作业 Key"""
        with self.cache_lock:
            self.job_cache[filename] = job_key

    def get_job_key(self, filename):
        """获取缓存的作业 Key"""
        with self.cache_lock:
            return self.job_cache.get(filename)

    def validate_config(self):
        """验证必要配置是否存在"""
        required_configs = [
            self.organization, self.tenant, self.pat,
            self.folder_id, self.robot_id
        ]

        # 检查是否有空值
        if not all(required_configs):
            missing = [name for name, value in zip(
                ["organization", "tenant", "pat", "folder_id", "robot_id"],
                required_configs
            ) if not value]

            error_msg = f"UiPath 配置不完整，缺少: {', '.join(missing)}"
            print(f"[ERROR] {error_msg}")
            # 改为警告而不是抛出异常，允许程序继续运行
            # raise ValueError(error_msg)

    def clear_cache(self):
        """清除所有缓存"""
        with self.cache_lock:
            self.job_cache = {}

    def get_all_jobs(self):
        """获取所有作业列表"""
        get_all_jobs_endpoint = f"{self.base_url}/odata/Jobs"

        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(self.folder_id)
        }

        try:
            response = requests.get(get_all_jobs_endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            jobs_data = response.json()
            jobs_list = jobs_data.get("value", [])

            return jobs_list
        except requests.exceptions.RequestException as e:
            error_msg = f"获取所有作业列表失败: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" | 错误信息: {error_details.get('message', '未知错误')}"
                except:
                    error_msg += f" | 响应文本: {e.response.text[:200]}"
            raise Exception(error_msg)

    def get_job_details_from_all_jobs(self, job_key_to_find):
        """
        从所有作业列表中查找特定的 job_key 并返回其详情
        这个方法解决了单独查询作业可能失败的问题
        """
        try:
            # 1. 获取所有 Jobs
            jobs_list = self.get_all_jobs()

            if not jobs_list:
                print(f"在文件夹 {self.folder_id} 中未找到任何作业")
                return None

            # 2. 从列表中查找特定的 Job Key
            found_job = None
            for job_item in jobs_list:
                if job_item.get("Key") == job_key_to_find:
                    found_job = job_item
                    break  # 找到后立即退出循环

            if found_job:
                print(f"找到作业: {job_key_to_find}, 状态: {found_job.get('State', 'Unknown')}")
                return found_job
            else:
                print(f"未在当前作业列表中找到 Job Key '{job_key_to_find}'。可能已完成或不在当前视图中。")
                return None

        except Exception as e:
            print(f"获取所有作业列表或查找特定作业失败: {e}")
            return None


# 全局 UiPath 实例
_uipath_instance = None
_instance_lock = threading.Lock()


def get_uipath_orchestrator():
    """获取或创建 UiPath Orchestrator 实例"""
    global _uipath_instance
    if _uipath_instance is None:
        with _instance_lock:
            if _uipath_instance is None:
                _uipath_instance = UiPathOrchestrator()
    return _uipath_instance


def reset_uipath_instance():
    """重置 UiPath 实例（用于配置变更后）"""
    global _uipath_instance
    with _instance_lock:
        _uipath_instance = None
