"""命令处理器测试"""

from unittest.mock import patch
from touchpad.handlers import (
    MoveCommandHandler,
    MouseDownCommandHandler,
    MouseUpCommandHandler,
    CommandDispatcher,
)


def test_move_command_handler():
    """测试移动命令处理器"""
    print("测试移动命令处理器...", end=" ")
    with patch("touchpad.handlers.mouse.pyautogui") as mock_pyautogui:
        handler = MoveCommandHandler()
        handler.execute(["10.5", "20.3"])
        mock_pyautogui.moveRel.assert_called_once_with(10.5, 20.3, duration=0)
    print("✓ 通过")


def test_mouse_down_handler():
    """测试鼠标按下处理器"""
    print("测试鼠标按下处理器...", end=" ")
    with patch("touchpad.handlers.mouse.pyautogui") as mock_pyautogui:
        handler = MouseDownCommandHandler("left")
        handler.execute([])
        mock_pyautogui.mouseDown.assert_called_once_with(button="left")
    print("✓ 通过")


def test_mouse_up_handler():
    """测试鼠标抬起处理器"""
    print("测试鼠标抬起处理器...", end=" ")
    with patch("touchpad.handlers.mouse.pyautogui") as mock_pyautogui:
        handler = MouseUpCommandHandler("right")
        handler.execute([])
        mock_pyautogui.mouseUp.assert_called_once_with(button="right")
    print("✓ 通过")


def test_command_dispatcher():
    """测试命令分发器"""
    print("测试命令分发器...", end=" ")
    with patch("touchpad.handlers.mouse.pyautogui") as mock_pyautogui:
        dispatcher = CommandDispatcher()

        # 测试移动命令
        dispatcher.dispatch("move", ["10", "20"])
        assert mock_pyautogui.moveRel.call_count == 1, "移动命令未正确分发"

        # 测试左键按下
        dispatcher.dispatch("left_down", [])
        assert mock_pyautogui.mouseDown.call_count == 1, "左键按下命令未正确分发"

        # 测试左键抬起
        dispatcher.dispatch("left_up", [])
        assert mock_pyautogui.mouseUp.call_count == 1, "左键抬起命令未正确分发"
    print("✓ 通过")


if __name__ == "__main__":
    test_move_command_handler()
    test_mouse_down_handler()
    test_mouse_up_handler()
    test_command_dispatcher()
    print("\n命令处理器测试全部通过！")
