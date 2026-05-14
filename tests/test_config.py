"""配置模块测试"""

from touchpad.config import Config, CommandConstants


def test_config_singleton():
    """测试配置单例"""
    print("测试配置单例...", end=" ")
    config1 = Config()
    config2 = Config()
    assert config1 is config2, "配置应该是单例"
    print("✓ 通过")


def test_config_defaults():
    """测试默认配置值"""
    print("测试默认配置值...", end=" ")
    config = Config()
    assert config.mouse_speed == 3.0, "mouse_speed 默认值错误"
    assert config.message_interval == 16, "message_interval 默认值错误"
    assert config.click_threshold == 1, "click_threshold 默认值错误"
    assert config.http_port == 9876, "http_port 默认值错误"
    assert config.websocket_port == 9877, "websocket_port 默认值错误"
    print("✓ 通过")


def test_command_constants():
    """测试命令常量"""
    print("测试命令常量...", end=" ")
    assert CommandConstants.MOVE == "move", "MOVE 常量错误"
    assert CommandConstants.LEFT_CLICK == "left_click", "LEFT_CLICK 常量错误"
    print("✓ 通过")


if __name__ == "__main__":
    test_config_singleton()
    test_config_defaults()
    test_command_constants()
    print("\n配置模块测试全部通过！")
