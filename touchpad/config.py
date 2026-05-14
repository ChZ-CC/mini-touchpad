"""配置模块

提供应用配置管理，使用单例模式确保全局唯一配置实例。
"""

import logging
import os
from typing import Final

import dotenv


class Config:
    """配置管理类"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        dotenv.load_dotenv()
        self.mouse_speed: float = float(os.getenv("MOUSE_SPEED", "3.0"))
        self.message_interval: int = int(os.getenv("MESSAGE_INTERVAL", "16"))
        self.click_threshold: int = int(os.getenv("CLICK_THRESHOLD", "1"))
        self.http_port: int = int(os.getenv("HTTP_PORT", "9876"))
        self.websocket_port: int = int(os.getenv("WEBSOCKET_PORT", "9877"))
        self.ping_interval: int = int(os.getenv("PING_INTERVAL", "30"))
        self.ping_timeout: int = int(os.getenv("PING_TIMEOUT", "3"))
        self.enable_ssl: bool = os.getenv("ENABLE_SSL", "false") in [
            "True",
            "true",
            "1",
            "t",
        ]
        self.ssl_cert_file: str = os.getenv("SSL_CERT_FILE", "cert.pem")
        self.ssl_key_file: str = os.getenv("SSL_KEY_FILE", "key.pem")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false") in [
            "True",
            "true",
            "1",
            "t",
        ]
        self.log_level = logging.INFO
        log_level: str = os.getenv("LOG_LEVEL", "INFO")
        if log_level.upper() == "DEBUG" or self.debug_mode:
            self.log_level = logging.DEBUG
        elif log_level.upper() == "WARNING":
            self.log_level = logging.WARNING
        elif log_level.upper() == "ERROR":
            self.log_level = logging.ERROR


class CommandConstants:
    """命令常量定义"""

    MOVE: Final[str] = "move"
    LEFT_CLICK: Final[str] = "left_click"
    RIGHT_CLICK: Final[str] = "right_click"
    SCROLL: Final[str] = "scroll"


config = Config()
__all__ = ["config", "CommandConstants"]
