"""命令处理模块

提供命令处理器和命令分发器，使用策略模式分离不同命令的处理逻辑。
"""

from .base import CommandHandler
from .mouse import (
    MoveCommandHandler,
    MouseClickCommandHandler,
)
from .dispatcher import CommandDispatcher

__all__ = [
    "CommandHandler",
    "MoveCommandHandler",
    "MouseClickCommandHandler",
    "CommandDispatcher",
]
