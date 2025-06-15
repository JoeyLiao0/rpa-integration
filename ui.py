import flet as ft
import json
import subprocess
import threading
import sys
import os
from datetime import datetime

class RPAIntegrationUI:
    # 封装一些函数
    def __init__(self):
        self.config_path = "config.json"
        self.current_process = None
        self.current_script = None
        self.page = None
        self.log_output = None
        self.config_data = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            error_message = f"配置文件未找到: {self.config_path}，请先创建配置文件！"
            if self.log_output:
                self.log_message(error_message, "error")
            raise FileNotFoundError(error_message)

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            self.log_message("配置保存成功！", "success")
        except Exception as e:
            self.log_message(f"配置保存失败: {e}", "error")

    def log_message(self, message, msg_type="info"):
        """添加日志消息"""
        if self.log_output:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            color = {
                "info": ft.colors.BLUE,
                "success": ft.colors.GREEN,
                "error": ft.colors.RED,
                "warning": ft.colors.ORANGE
            }.get(msg_type, ft.colors.BLACK)

            log_entry = ft.Text(
                f"[{timestamp}] {message}",
                color=color,
                size=12
            )
            self.log_output.controls.append(log_entry)
            if len(self.log_output.controls) > 100:  # 限制日志数量
                self.log_output.controls.pop(0)
            self.log_output.scroll_to(offset=-1)
            self.page.update()

    def create_config_form(self):
        """创建配置表单"""
        config_fields = []

        # 路径配置
        config_fields.append(ft.Text("路径配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="触发文件夹路径",
            value=self.config_data["paths"]["trigger_folder"],
            on_change=lambda e: self.update_config_value("paths.trigger_folder", e.control.value)
        ))

        # Web配置
        config_fields.append(ft.Divider(height=20))
        config_fields.append(ft.Text("Web配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="任务列表URL",
            value=self.config_data["web"]["task_list_url"],
            on_change=lambda e: self.update_config_value("web.task_list_url", e.control.value)
        ))
        config_fields.append(ft.TextField(
            label="登录用户名",
            value=self.config_data["web"]["login_username"],
            on_change=lambda e: self.update_config_value("web.login_username", e.control.value)
        ))
        config_fields.append(ft.TextField(
            label="登录密码",
            value=self.config_data["web"]["login_password"],
            password=True,
            can_reveal_password=True, # 密文与可视按钮
            on_change=lambda e: self.update_config_value("web.login_password", e.control.value)
        ))

        # 服务器配置
        config_fields.append(ft.Divider(height=20))
        config_fields.append(ft.Text("服务器配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="服务器主机",
            value=self.config_data["server"]["host"],
            on_change=lambda e: self.update_config_value("server.host", e.control.value)
        ))
        config_fields.append(ft.TextField(
            label="服务器端口",
            value=str(self.config_data["server"]["port"]),
            on_change=lambda e: self.update_config_value("server.port",
                                                         int(e.control.value) if e.control.value.isdigit() else 55332)
        ))
        config_fields.append(ft.TextField(
            label="最大连接数",
            value=str(self.config_data["server"]["max_connections"]),
            on_change=lambda e: self.update_config_value("server.max_connections",
                                                         int(e.control.value) if e.control.value.isdigit() else 5)
        ))
        config_fields.append(ft.TextField(
            label="客户端主机",
            value=self.config_data["server"]["client_host"],
            on_change=lambda e: self.update_config_value("server.client_host", e.control.value)
        ))

        # UI配置
        config_fields.append(ft.Divider(height=20))
        config_fields.append(ft.Text("UI配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="API URL",
            value=self.config_data["ui"]["api_url"],
            on_change=lambda e: self.update_config_value("ui.api_url", e.control.value)
        ))
        config_fields.append(ft.TextField(
            label="用户名",
            value=self.config_data["ui"]["username"],
            on_change=lambda e: self.update_config_value("ui.username", e.control.value)
        ))
        config_fields.append(ft.TextField(
            label="API密钥",
            value=self.config_data["ui"]["api_key"],
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.update_config_value("ui.api_key", e.control.value)
        ))

        # Selenium配置
        config_fields.append(ft.Divider(height=20))
        config_fields.append(ft.Text("Selenium配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="隐式等待时间(秒)",
            value=str(self.config_data["selenium"]["implicit_wait_time"]),
            on_change=lambda e: self.update_config_value("selenium.implicit_wait_time",
                                                         int(e.control.value) if e.control.value.isdigit() else 10)
        ))
        config_fields.append(ft.TextField(
            label="显式等待时间(秒)",
            value=str(self.config_data["selenium"]["explicit_wait_time"]),
            on_change=lambda e: self.update_config_value("selenium.explicit_wait_time",
                                                         int(e.control.value) if e.control.value.isdigit() else 20)
        ))
        config_fields.append(ft.TextField(
            label="轮询频率(秒)",
            value=str(self.config_data["selenium"]["poll_frequency"]),
            on_change=lambda e: self.update_config_value("selenium.poll_frequency",
                                                         float(e.control.value) if e.control.value.replace('.',
                                                                                                           '').isdigit() else 0.5)
        ))

        # 时间配置
        config_fields.append(ft.Divider(height=20))
        config_fields.append(ft.Text("时间配置", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE))
        config_fields.append(ft.TextField(
            label="睡眠间隔(秒)",
            value=str(self.config_data["timing"]["sleep_interval"]),
            on_change=lambda e: self.update_config_value("timing.sleep_interval",
                                                         int(e.control.value) if e.control.value.isdigit() else 60)
        ))
        config_fields.append(ft.TextField(
            label="短睡眠时间(秒)",
            value=str(self.config_data["timing"]["short_sleep"]),
            on_change=lambda e: self.update_config_value("timing.short_sleep",
                                                         int(e.control.value) if e.control.value.isdigit() else 2)
        ))
        config_fields.append(ft.TextField(
            label="RPA检查间隔(秒)",
            value=str(self.config_data["timing"]["rpa_check_interval"]),
            on_change=lambda e: self.update_config_value("timing.rpa_check_interval",
                                                         int(e.control.value) if e.control.value.isdigit() else 2)
        ))

        # 保存按钮
        config_fields.append(ft.Divider(height=30))
        config_fields.append(ft.ElevatedButton(
            "保存配置",
            icon=ft.icons.SAVE,
            on_click=lambda e: self.save_config(),
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_600
            )
        ))

        return ft.Column(
            controls=config_fields,
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )

    def update_config_value(self, key_path, value):
        """更新配置值"""
        keys = key_path.split('.')
        current = self.config_data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def run_script(self, script_name):
        """运行脚本"""
        if self.current_process and self.current_process.poll() is None:
            self.log_message("已有脚本在运行中，请先停止当前脚本！", "warning")
            return

        if not os.path.exists(script_name):
            self.log_message(f"脚本文件 {script_name} 不存在！", "error")
            return

        try:
            self.current_script = script_name
            self.log_message(f"开始运行脚本: {script_name}", "info")

            # 在新线程中运行脚本
            thread = threading.Thread(target=self._run_script_thread, args=(script_name,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.log_message(f"运行脚本失败: {e}", "error")

    def _run_script_thread(self, script_name):
        """在线程中运行脚本"""
        # 线程创建一个子进程subprocess
        # 不异步运行ui就会卡住
        try:
            self.current_process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 读取输出
            for line in iter(self.current_process.stdout.readline, ''): # 直到返回空串
                if line:
                    self.log_message(f"[{self.current_script}] {line.strip()}", "info")

            self.current_process.wait()
            if self.current_process.returncode == 0:
                self.log_message(f"脚本 {script_name} 执行完成", "success")
            else:
                self.log_message(f"脚本 {script_name} 执行失败，返回码: {self.current_process.returncode}", "error")

        except Exception as e:
            self.log_message(f"脚本执行异常: {e}", "error")
        finally:
            self.current_process = None
            self.current_script = None

    def stop_script(self):
        """停止当前运行的脚本"""
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.log_message(f"脚本 {self.current_script} 已停止", "warning")
            except Exception as e:
                self.log_message(f"停止脚本失败: {e}", "error")
        else:
            self.log_message("没有正在运行的脚本", "info")

    def clear_log(self):
        """清空日志"""
        if self.log_output:
            self.log_output.controls.clear()
            self.page.update()

    def create_run_view(self):
        """创建运行视图"""
        # IOP区域
        iop_section = ft.Column([
            ft.Text("IOP", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
            ft.Container(height=15),  # 间距
            ft.ElevatedButton(
                "运行 IOP Client",
                icon=ft.icons.PLAY_ARROW,
                height=45,
                width=180,
                on_click=lambda e: self.run_script("IOP_integration/client.py"),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_400,
                    text_style=ft.TextStyle(size=14)
                )
            ),
        ], spacing=0)

        # IBP区域
        ibp_section = ft.Column([
            ft.Text("IBP", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
            ft.Container(height=15),  # 间距
            ft.ElevatedButton(
                "运行 IBP Client",
                icon=ft.icons.PLAY_ARROW,
                height=45,
                width=180,
                on_click=lambda e: self.run_script("IBP_integration/client_rpa.py"),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_400,
                    text_style=ft.TextStyle(size=14)
                )
            ),
            ft.Container(height=12),  # 按钮间距
            ft.ElevatedButton(
                "运行 IBP Service",
                icon=ft.icons.PLAY_ARROW,
                height=45,
                width=180,
                on_click=lambda e: self.run_script("IBP_integration/service_user.py"),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_400,
                    text_style=ft.TextStyle(size=14)
                )
            ),
        ], spacing=0)

        # 底部控制按钮
        bottom_controls = ft.Column([
            ft.ElevatedButton(
                "停止脚本",
                icon=ft.icons.STOP,
                height=45,
                width=180,
                on_click=lambda e: self.stop_script(),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED_300,
                    text_style=ft.TextStyle(size=14)
                )
            ),
            ft.Container(height=12),  # 按钮间距
            ft.ElevatedButton(
                "清空日志",
                icon=ft.icons.CLEAR,
                height=45,
                width=180,
                on_click=lambda e: self.clear_log(),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.ORANGE_300,
                    text_style=ft.TextStyle(size=14)
                )
            )
        ], spacing=0)

        # 脚本控制面板
        script_controls = ft.Column([
            iop_section,
            ft.Container(height=30),  # 区域间距
            ibp_section,
            ft.Container(expand=True),  # 占据剩余空间，将底部控制推到底部
            bottom_controls
        ], spacing=0, expand=True)

        # 日志输出区域
        self.log_output = ft.Column([], scroll=ft.ScrollMode.AUTO, spacing=2)
        log_container = ft.Container(
            content=self.log_output,
            bgcolor=ft.colors.GREY_50,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=10,
            width=900, # None为自适应
            height=600,  # 固定高度
        )

        return ft.Row([
            ft.Container(
                content=script_controls,
                width=220,
                padding=ft.padding.all(15),
                height=700
            ),
            ft.VerticalDivider(width=1),
            ft.Container(
                content=ft.Column([
                    ft.Text("运行日志", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                    log_container
                ], spacing=10),
                expand=True,
                padding=10
            )
        ], expand=True)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "RPA Integation"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 1200
        page.window.height = 800
        page.window.min_width = 800
        page.window.min_height = 600
        page.window.maximizable = False # 最大化禁止

        def nav_click(nav_item, view_content):# 在main内定义 才能用nav_rail等容器
            # 更新导航样式
            for nav in nav_rail.controls:
                if hasattr(nav, 'bgcolor'):
                    nav.bgcolor = ft.colors.TRANSPARENT
            nav_item.bgcolor = ft.colors.BLUE_100

            # 更新内容区域
            content_area.content = view_content
            page.update()

        # 导航栏
        config_nav = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SETTINGS, color=ft.colors.BLUE_600),
                ft.Text("配置", size=16, color=ft.colors.BLUE_600)
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border_radius=8,
            bgcolor=ft.colors.BLUE_100,
            on_click=lambda e: nav_click(config_nav, self.create_config_form())
        )

        run_nav = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PLAY_CIRCLE, color=ft.colors.BLUE_600),
                ft.Text("运行", size=16, color=ft.colors.BLUE_600)
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border_radius=8,
            bgcolor=ft.colors.TRANSPARENT,
            on_click=lambda e: nav_click(run_nav, self.create_run_view())
        )

        nav_rail = ft.Column([
            ft.Container(
                content=ft.Text("RPA-integration", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                padding=ft.padding.symmetric(horizontal=15, vertical=20)
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            config_nav,
            run_nav
        ], spacing=5)

        # 内容区域
        content_area = ft.Container(
            content=self.create_config_form(),  # 默认显示配置页面，后续可以改一个欢迎界面
            expand=True,
            padding=20
        )

        # 主布局
        main_layout = ft.Row([
            ft.Container(
                content=nav_rail,
                width=200,
                # bgcolor=ft.colors.GREY_50,
                border=ft.border.only(right=ft.BorderSide(1, ft.colors.GREY_300)),
                padding=ft.padding.only(top=10, bottom=10)
            ),
            content_area
        ], expand=True)

        page.add(main_layout)

        # 初始化日志
        self.log_message("RPA Integration 系统已启动", "success")


def main(page: ft.Page):
    app = RPAIntegrationUI()
    app.main(page)


if __name__ == "__main__":
    ft.app(target=main)