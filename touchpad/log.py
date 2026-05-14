"""日志配置模块

提供统一的日志配置和管理。
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from touchpad.config import config


class Logger:
    """日志管理器"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "touchpad") -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(config.log_level)

        # 阻止日志传播到父 logger，避免重复记录
        logger.propagate = False

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 文件处理器 - 所有级别都写入文件
        file_handler = cls.windows_compatible_handler(log_dir / "touchpad.log")
        file_handler.setLevel(config.log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.log_level)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def windows_compatible_handler(cls, filename):
        """创建适合 Windows 的日志处理器，解决文件锁定问题"""
        import os

        class WindowsSafeRotatingFileHandler(RotatingFileHandler):
            def doRollover(self):
                """重写日志轮转方法以解决 Windows 文件锁定问题"""
                if self.stream:
                    self.stream.close()
                    self.stream = None

                # 检查基础文件是否存在
                if os.path.exists(self.baseFilename):
                    # 轮转备份文件
                    for i in range(self.backupCount - 1, 0, -1):
                        sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                        dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
                        if os.path.exists(sfn):
                            if os.path.exists(dfn):
                                os.unlink(dfn)  # 使用 unlink 替代 remove
                            os.rename(sfn, dfn)

                    # 重命名当前日志文件
                    dfn = self.rotation_filename(f"{self.baseFilename}.1")
                    if os.path.exists(dfn):
                        os.unlink(dfn)  # 使用 unlink 替代 remove
                    os.rename(self.baseFilename, dfn)

                # 重新打开流
                self.stream = self._open()

        return WindowsSafeRotatingFileHandler(
            filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
            delay=True,  # 延迟打开文件直到第一次写入
        )


def get_logger(name: str = "touchpad") -> logging.Logger:
    """获取日志记录器的便捷函数

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return Logger.get_logger(name)


__all__ = ["Logger", "get_logger"]
