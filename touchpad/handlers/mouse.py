"""鼠标命令处理器

提供鼠标移动、按下、抬起等命令的具体实现。
"""

from typing import List

import pynput
from pynput.mouse import Button

from .base import CommandHandler

mouse = pynput.mouse.Controller()


class MoveCommandHandler(CommandHandler):
    """移动命令处理器"""

    def execute(self, args: List[str]) -> None:
        if len(args) == 2:
            dx = int(float(args[0]))
            dy = int(float(args[1]))
            mouse.move(dx, dy)


class MouseDownCommandHandler(CommandHandler):
    """鼠标按下命令处理器"""

    def __init__(self, button: Button):
        self.button = button

    def execute(self, args: List[str]) -> None:
        mouse.press(button=self.button)


class MouseUpCommandHandler(CommandHandler):
    """鼠标抬起命令处理器"""

    def __init__(self, button: Button):
        self.button = button

    def execute(self, args: List[str]) -> None:
        mouse.release(button=self.button)


class ScrollCommandHandler(CommandHandler):
    """滚动命令处理器"""

    def execute(self, args: List[str]) -> None:
        if len(args) > 1:
            dx = int(float(args[0]))
            dy = int(float(args[1]))
            mouse.scroll(dx, dy)
