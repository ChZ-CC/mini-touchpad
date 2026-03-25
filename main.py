"""Touchpad - 手机触控板应用

主入口文件
"""

import pyautogui

from touchpad.app import main as app_main

pyautogui.FAILSAFE = False


if __name__ == "__main__":
    import asyncio

    asyncio.run(app_main())
