"""命令处理器基类

定义命令处理器的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List


class CommandHandler(ABC):
    """命令处理器抽象基类

    所有命令处理器都必须继承此类并实现 execute 方法。
    """

    @abstractmethod
    def execute(self, args: List[str]) -> None:
        """执行命令

        Args:
            args: 命令参数列表
        """
        pass
