"""命令分发器

使用职责链模式统一调度命令处理器。
"""

from typing import Dict, List
from .base import CommandHandler
from .mouse import (
    MoveCommandHandler,
    MouseDownCommandHandler,
    MouseUpCommandHandler,
    ScrollCommandHandler,
)
from touchpad.config import CommandConstants
from touchpad.log import get_logger

logger = get_logger(__name__)


class CommandDispatcher:
    """命令分发器

    负责将命令分发到对应的处理器执行。
    """

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """注册所有命令处理器"""
        self._handlers[CommandConstants.MOVE] = MoveCommandHandler()
        self._handlers[CommandConstants.LEFT_DOWN] = MouseDownCommandHandler("left")
        self._handlers[CommandConstants.LEFT_UP] = MouseUpCommandHandler("left")
        self._handlers[CommandConstants.RIGHT_DOWN] = MouseDownCommandHandler("right")
        self._handlers[CommandConstants.RIGHT_UP] = MouseUpCommandHandler("right")
        self._handlers[CommandConstants.SCROLL] = ScrollCommandHandler()

    def dispatch(self, command: str, args: List[str]) -> None:
        """分发命令到对应的处理器

        Args:
            command: 命令类型
            args: 命令参数列表
        """
        handler = self._handlers.get(command)
        if handler:
            logger.debug(f"分发命令: {command}, 参数: {args}")
            handler.execute(args)
        else:
            logger.warning(f"未知指令：{command}, 参数：{args}")
