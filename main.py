"""Touchpad - 手机触控板应用

主入口文件
"""

import sys
import pyautogui
import asyncio

from touchpad.app import app

pyautogui.FAILSAFE = False


if __name__ == "__main__":
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        sys.exit(0)
