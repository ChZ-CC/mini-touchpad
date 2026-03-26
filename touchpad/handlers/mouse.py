"""鼠标命令处理器

提供鼠标移动、按下、抬起等命令的具体实现。
"""

import pyautogui
from typing import List
from .base import CommandHandler


class MoveCommandHandler(CommandHandler):
    """移动命令处理器"""

    def execute(self, args: List[str]) -> None:
        if len(args) == 2:
            dx = float(args[0])
            dy = float(args[1])
            pyautogui.moveRel(dx, dy, duration=0)


class MouseDownCommandHandler(CommandHandler):
    """鼠标按下命令处理器"""

    def __init__(self, button: str):
        self.button = button

    def execute(self, args: List[str]) -> None:
        pyautogui.mouseDown(button=self.button)


class MouseUpCommandHandler(CommandHandler):
    """鼠标抬起命令处理器"""

    def __init__(self, button: str):
        self.button = button

    def execute(self, args: List[str]) -> None:
        pyautogui.mouseUp(button=self.button)


class ScrollCommandHandler(CommandHandler):
    """滚动命令处理器"""

    def execute(self, args: List[str]) -> None:
        if len(args) == 1:
            amount = int(args[0])
            pyautogui.scroll(amount)
