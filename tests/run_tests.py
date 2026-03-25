"""测试运行器

运行所有测试并生成报告
"""

import sys


from tests.test_config import (
    test_config_singleton,
    test_config_defaults,
    test_command_constants,
)
from tests.test_handlers import (
    test_move_command_handler,
    test_mouse_down_handler,
    test_mouse_up_handler,
    test_command_dispatcher,
)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("运行 Touchpad 应用测试")
    print("=" * 50 + "\n")

    tests = [
        # 配置测试
        test_config_singleton,
        test_config_defaults,
        test_command_constants,
        # 处理器测试
        test_move_command_handler,
        test_mouse_down_handler,
        test_mouse_up_handler,
        test_command_dispatcher,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ 错误: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
