"""命令处理器测试"""

from unittest.mock import patch, MagicMock

from pynput.mouse import Button
from pynput import mouse
from touchpad.handlers import (
    MoveCommandHandler,
    MouseClickCommandHandler,
    CommandDispatcher,
)


def test_move_command_handler():
    """测试移动命令处理器"""
    print("测试移动命令处理器...", end=" ")
    with patch("touchpad.handlers.mouse.mouse") as mock_mouse:
        handler = MoveCommandHandler()
        handler.execute(["10.5", "20.3"])
        mock_mouse.move.assert_called_once_with(10, 20)
    print("✓ 通过")


def test_mouse_click_handler():
    """测试鼠标点击处理器"""
    print("测试鼠标点击处理器...", end=" ")
    with patch("touchpad.handlers.mouse.mouse") as mock_mouse:
        handler = MouseClickCommandHandler(Button.left)
        handler.execute([])
        assert mock_mouse.press.call_count == 1, "鼠标按下未被调用"
        assert mock_mouse.release.call_count == 1, "鼠标抬起未被调用"
    print("✓ 通过")


def test_scroll_command_handler():
    """测试滚动命令处理器"""
    print("测试滚动命令处理器...", end=" ")
    with patch("touchpad.handlers.mouse.mouse") as mock_mouse:
        handler = __import__(
            "touchpad.handlers.mouse"
        ).handlers.mouse.ScrollCommandHandler()
        handler.execute(["0", "5"])
        mock_mouse.scroll.assert_called_once_with(0, 5)
    print("✓ 通过")


def test_command_dispatcher():
    """测试命令分发器"""
    print("测试命令分发器...", end=" ")
    with patch("touchpad.handlers.mouse.mouse") as mock_mouse:
        dispatcher = CommandDispatcher()

        # 测试移动命令
        dispatcher.dispatch("move", ["10", "20"])
        assert mock_mouse.move.call_count == 1, "移动命令未正确分发"

        # 测试左键点击
        dispatcher.dispatch("left_click", [])
        assert mock_mouse.press.call_count == 1, "左键按下命令未正确分发"
        assert mock_mouse.release.call_count == 1, "左键抬起命令未正确分发"
    print("✓ 通过")


if __name__ == "__main__":
    test_move_command_handler()
    test_mouse_click_handler()
    test_scroll_command_handler()
    test_command_dispatcher()
    print("\n命令处理器测试全部通过！")
