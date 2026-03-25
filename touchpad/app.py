"""应用主类

整合所有模块，提供应用入口。
"""

from datetime import datetime

from .config import config
from .handlers import CommandDispatcher
from .log import get_logger
from .network import start_websocket_server
from .network import start_http_server
from .utils import get_local_ip

logger = get_logger(__name__)
print(logger)


class TouchpadApplication:
    """触控板应用主类

    整合所有模块，协调各组件工作。
    """

    def __init__(self):
        self._command_dispatcher = CommandDispatcher()

    async def _handle_message(self, message: str) -> None:
        """处理接收到的消息

        Args:
            message: 接收到的消息
        """
        now = datetime.now()
        logger.debug(f"收到消息[{now}]: {message}")

        parts = message.split("|")
        if len(parts) < 1:
            return

        command = parts[0]
        args = parts[1].split(",") if len(parts) > 1 else []

        start_time = datetime.now()
        self._command_dispatcher.dispatch(command, args)
        elapsed = datetime.now() - start_time
        logger.debug(f"处理耗时: {elapsed}")

    def _print_startup_info(self) -> None:
        """打印启动信息"""
        if config.debug_mode:
            logger.debug("调试模式已启用")
            print(
                f"当前配置：\n"
                f"\tMOUSE_SPEED={config.mouse_speed}\n"
                f"\tMESSAGE_INTERVAL={config.message_interval}\n"
                f"\tCLICK_THRESHOLD={config.click_threshold}\n"
                f"\tHTTP_PORT={config.http_port}\n"
                f"\tWEBSOCKET_PORT={config.websocket_port}"
            )
        ip = get_local_ip()
        print("=== 手机触控板服务已启动 ===")
        print(f"1. 电脑IP地址：{ip}")
        print(f"2. 手机浏览器访问：http://{ip}:{config.http_port}")
        print("3. 确保手机和电脑连接同一WiFi")

    async def run(self) -> None:
        """运行应用"""
        self._print_startup_info()
        start_http_server(host="0.0.0.0", port=config.http_port)
        await start_websocket_server(self._handle_message, config)


async def main():
    """主函数"""
    logger.info("启动触控板应用")
    app = TouchpadApplication()
    await app.run()


__all__ = ["TouchpadApplication", "main"]
