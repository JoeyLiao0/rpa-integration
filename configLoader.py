import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_path: str = "E:\\python_file\\rpa\\config.json"):
        # 初始化
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        # 加载配置文件
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"读取配置文件失败: {e}")

    def reload_config(self) -> None:
        # 重新加载
        self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        # 获取配置项
        if self._config is None:
            return default

        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy() if self._config else {}

    # === 路径配置 ===
    def get_trigger_folder_path(self) -> str:
        """获取触发文件夹路径"""
        return self.get('paths.trigger_folder', 'D:\\WorkSpace\\Python\\rpa\\')

    def get_rpa_filename_excel_path(self) -> str:
        """获取RPA文件名Excel路径"""
        return self.get('paths.rpa_filename_excel', 'D:\\WorkSpace\\Python\\rpa\\rpa_filename.xlsx')

    # === Web配置 ===
    def get_task_list_url(self) -> str:
        """获取任务列表URL"""
        return self.get('web.task_list_url', 'http://localhost:8080/tasklist')

    def get_login_username(self) -> str:
        """获取登录用户名"""
        return self.get('web.login_username', 'demo')

    def get_login_password(self) -> str:
        """获取登录密码"""
        return self.get('web.login_password', 'demo')

    # === 服务器配置 ===
    def get_server_host(self) -> str:
        """获取服务器主机地址"""
        return self.get('server.host', '0.0.0.0')

    def get_server_port(self) -> int:
        """获取服务器端口"""
        return self.get('server.port', 55332)

    def get_max_connections(self) -> int:
        """获取最大连接数"""
        return self.get('server.max_connections', 5)

    def get_client_host(self) -> str:
        """获取客户端主机地址"""
        return self.get('server.client_host', '127.0.0.1')

    # === RPA文件名映射 ===
    def get_rpa_filename_mapping(self) -> Dict[str, str]:
        """获取RPA文件名映射"""
        return self.get('rpa_filename_mapping', {})

    # === Superman项目配置 ===
    def get_superman_items(self) -> Dict[str, str]:
        """获取Superman项目配置"""
        return self.get('superman_items', {})

    # === UI配置 ===
    def get_api_url(self) -> str:
        return self.get('api.base_url', self.get('ui.api_url', ''))

    def get_username(self) -> str:
        return self.get('api.username', self.get('ui.username', ''))

    def get_api_key(self) -> str:
        return self.get('api.password', self.get('ui.api_key', ''))

    def get_api_platform(self) -> str:
        return self.get('api.platform', 'camunda7')

    def get_implicit_wait_time(self) -> int:
        """获取隐式等待时间"""
        return self.get('selenium.implicit_wait_time', 10)

    def get_explicit_wait_time(self) -> int:
        """获取显式等待时间"""
        return self.get('selenium.explicit_wait_time', 20)

    def get_poll_frequency(self) -> float:
        """获取轮询频率"""
        return self.get('selenium.poll_frequency', 0.5)

    # === 时间配置 ===
    def get_sleep_interval(self) -> int:
        """获取睡眠间隔"""
        return self.get('timing.sleep_interval', 60)

    def get_short_sleep(self) -> int:
        """获取短睡眠时间"""
        return self.get('timing.short_sleep', 2)

    def get_rpa_check_interval(self) -> int:
        """获取RPA检查间隔"""
        return self.get('timing.rpa_check_interval', 2)

    # === 配置更新方法 ===
    def update_config(self, key: str, value: Any) -> None:
        if self._config is None:
            self._config = {}

        keys = key.split('.')
        current = self._config

        # 导航到目标位置
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # 设置值
        current[keys[-1]] = value

        # 保存到文件
        self.save_config()

    def save_config(self) -> None:
        """保存配置到文件"""
        if self._config is None:
            return

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {e}")


# 全局配置实例
config = ConfigLoader()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置项"""
    return config.get(key, default)


def reload_config() -> None:
    """重新加载配置"""
    config.reload_config()


def update_config(key: str, value: Any) -> None:
    """更新配置"""
    config.update_config(key, value)