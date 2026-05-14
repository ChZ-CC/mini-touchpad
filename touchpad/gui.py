"""电脑端服务界面

提供启动和停止服务功能，以及配置信息的修改。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from datetime import datetime
from touchpad.app import TouchpadApplication
from touchpad.config import config
from touchpad.utils import get_local_ip
from touchpad.log import get_logger

logger = get_logger(__name__)


class TouchpadGUI:
    """触控板服务界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("Touchpad - 手机触控板服务")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.app = None
        self.loop = None
        self.thread = None
        self.running = False

        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 服务状态区域
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding="10")
        status_frame.pack(fill=tk.X, pady=5)

        # 状态行
        status_row = ttk.Frame(status_frame)
        status_row.pack(fill=tk.X, pady=2)
        self.status_var = tk.StringVar(value="未启动")
        ttk.Label(status_row, text="当前状态:", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            status_row, textvariable=self.status_var, width=20, foreground="red"
        ).pack(side=tk.LEFT, padx=5)

        # IP地址行
        ip_row = ttk.Frame(status_frame)
        ip_row.pack(fill=tk.X, pady=2)
        self.ip_var = tk.StringVar(value=f"IP地址: {get_local_ip()}")
        ttk.Label(ip_row, textvariable=self.ip_var).pack(side=tk.LEFT, padx=5)

        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(
            control_frame, text="启动服务", command=self.start_service, width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="停止服务",
            command=self.stop_service,
            width=15,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置信息", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 配置项
        config_items = [
            ("消息间隔(ms)", "message_interval", 1, 100, 1),
            ("点击阈值(像素)", "click_threshold", 1, 50, 1),
            ("HTTP端口", "http_port", 1024, 65535, 1),
            ("WebSocket端口", "websocket_port", 1024, 65535, 1),
        ]

        self.config_vars = {}
        for i, (label, config_name, min_val, max_val, step) in enumerate(config_items):
            row = ttk.Frame(config_frame)
            row.pack(fill=tk.X, pady=2)

            ttk.Label(row, text=label, width=15).pack(side=tk.LEFT, padx=5)

            var = tk.DoubleVar(value=getattr(config, config_name))
            self.config_vars[config_name] = var

            entry = ttk.Entry(row, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)

        # 调试模式
        debug_frame = ttk.Frame(config_frame)
        debug_frame.pack(fill=tk.X, pady=2)

        ttk.Label(debug_frame, text="调试模式", width=15).pack(side=tk.LEFT, padx=5)
        self.debug_var = tk.BooleanVar(value=config.debug_mode)
        ttk.Checkbutton(debug_frame, variable=self.debug_var).pack(side=tk.LEFT, padx=5)

        # 应用配置按钮
        ttk.Button(config_frame, text="应用配置", command=self.apply_config).pack(
            pady=10
        )

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _update_status(self):
        """更新服务状态"""
        if self.running:
            self.status_var.set("运行中")
            self.status_var.set("运行中")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_var.set("未启动")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def _log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_service(self):
        """启动服务"""
        if self.running:
            messagebox.showinfo("提示", "服务已经在运行中")
            return

        try:
            self._log("正在启动服务...")

            # 应用配置
            self.apply_config()

            # 创建事件循环
            self.loop = asyncio.new_event_loop()

            # 启动服务线程
            self.thread = threading.Thread(target=self._run_service, daemon=True)
            self.thread.start()

            # 延迟更新状态
            self.root.after(1000, self._update_after_start)

        except Exception as e:
            self._log(f"启动服务失败: {e}")
            messagebox.showerror("错误", f"启动服务失败: {e}")

    def _run_service(self):
        """在线程中运行服务"""
        asyncio.set_event_loop(self.loop)
        self.app = TouchpadApplication()
        try:
            self.loop.run_until_complete(self.app.run())
        except Exception as e:
            self._log(f"服务运行出错: {e}")

    def _update_after_start(self):
        """启动后的状态更新"""
        self.running = True
        self._update_status()
        self._log("服务启动成功")
        self._log(f"手机浏览器访问: http://{get_local_ip()}:{config.http_port}")

    def stop_service(self):
        """停止服务"""
        if not self.running:
            messagebox.showinfo("提示", "服务未启动")
            return

        try:
            self._log("正在停止服务...")

            # 停止事件循环
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)

            # 等待线程结束
            if self.thread:
                self.thread.join(timeout=5)

            # 清理资源
            self.loop = None
            self.thread = None
            self.app = None

            self.running = False
            self._update_status()
            self._log("服务已停止")

        except Exception as e:
            self._log(f"停止服务失败: {e}")
            messagebox.showerror("错误", f"停止服务失败: {e}")

    def apply_config(self):
        """应用配置"""
        try:
            # 更新配置
            for config_name, var in self.config_vars.items():
                value = var.get()
                if config_name in [
                    "http_port",
                    "websocket_port",
                    "message_interval",
                    "click_threshold",
                ]:
                    value = int(value)
                setattr(config, config_name, value)

            # 更新调试模式
            config.debug_mode = self.debug_var.get()

            self._log("配置已更新")
            messagebox.showinfo("提示", "配置已更新")

        except Exception as e:
            self._log(f"更新配置失败: {e}")
            messagebox.showerror("错误", f"更新配置失败: {e}")


def main():
    """启动GUI"""
    root = tk.Tk()
    app = TouchpadGUI(root)

    # 处理窗口关闭
    def on_close():
        if app.running:
            app.stop_service()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
