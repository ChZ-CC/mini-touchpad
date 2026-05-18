"""电脑端服务界面

提供启动和停止服务功能，以及配置信息的修改。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from datetime import datetime
from touchpad.app import TouchpadApplication
from touchpad.log import get_logger
from touchpad.config import Config, config

logger = get_logger(__name__)


class TouchpadGUI:
    """触控板服务界面"""

    def __init__(self, root, config: Config = config):
        self.root = root
        self.root.title("Touchpad - 手机触控板服务")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.app = None
        self.loop = None
        self.thread = None
        self.running = False

        self.config = config
        self.config_vars = {}
        self.status_var = tk.StringVar(value="未启动")
        self.url_var = tk.StringVar(value="")

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
        ttk.Label(status_row, text="当前状态:", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            status_row, textvariable=self.status_var, width=20, foreground="red"
        ).pack(side=tk.LEFT, padx=5)

        # IP地址行
        ip_row = ttk.Frame(status_frame)
        ip_row.pack(fill=tk.X, pady=2)
        ttk.Label(ip_row, text="服务地址:", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(ip_row, textvariable=self.url_var).pack(side=tk.LEFT, padx=5)

        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置信息", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 配置项
        self._create_form(
            config_frame,
            "message_interval",
            "消息间隔(ms)",
            self.config.message_interval,
        )
        self._create_form(
            config_frame,
            "click_threshold",
            "点击阈值(像素)",
            self.config.click_threshold,
        )
        self._create_form(
            config_frame,
            "http_port",
            "HTTP端口",
            self.config.http_port,
        )
        self._create_form(
            config_frame,
            "websocket_port",
            "WebSocket端口",
            self.config.websocket_port,
        )

        # 调试模式
        debug_frame = ttk.Frame(config_frame)
        debug_frame.pack(fill=tk.X, pady=2)

        ttk.Label(debug_frame, text="调试模式", width=15).pack(side=tk.LEFT, padx=5)
        self.debug_var = tk.BooleanVar(value=self.config.debug_mode)
        ttk.Checkbutton(debug_frame, variable=self.debug_var).pack(side=tk.LEFT, padx=5)

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

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _create_form(self, parent, var_name, label_text, default_value):
        """创建表单行"""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)

        ttk.Label(row, text=label_text, width=15).pack(side=tk.LEFT, padx=5)

        var = tk.IntVar(value=default_value)
        entry = ttk.Entry(row, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        self.config_vars[var_name] = var

    def _update_status(self):
        """更新服务状态"""
        if self.running:
            self.status_var.set("运行中")
            self.url_var.set(self.app.http_url if self.app else "")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_var.set("未启动")
            self.url_var.set("")
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
        self.app = TouchpadApplication(config=self.config)
        try:
            self.loop.run_until_complete(self.app.run())
        except Exception as e:
            self._log(f"服务运行出错: {e}")

    def _update_after_start(self):
        """启动后的状态更新"""
        self.running = True
        self._update_status()
        self._log("服务启动成功")
        self._log(f"手机浏览器访问: {self.url_var.get()}")

    def stop_service(self):
        """停止服务"""
        if not self.running:
            messagebox.showinfo("提示", "服务未启动")
            return

        try:
            self._log("正在停止服务...")

            if self.app:
                if self.loop and self.loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self.app.close(), self.loop
                    )
                    # 等待关闭完成
                    future.result(timeout=5)

            # 停止事件循环
            if self.loop and self.loop.is_running():
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
            self.config.http_port = self.config_vars["http_port"].get()
            self.config.websocket_port = self.config_vars["websocket_port"].get()
            self.config.message_interval = self.config_vars["message_interval"].get()
            self.config.click_threshold = self.config_vars["click_threshold"].get()

            # 更新调试模式
            self.config.debug_mode = self.debug_var.get()

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
