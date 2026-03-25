"""WebSocket服务器

提供WebSocket连接管理和消息处理功能。
"""

import asyncio
import websockets
from typing import Callable, Awaitable
from touchpad.config import Config
from touchpad.log import get_logger

logger = get_logger(__name__)


class WebSocketConnection:
    """WebSocket连接管理

    管理单个WebSocket连接的生命周期。
    """

    def __init__(
        self,
        message_handler: Callable[[str], Awaitable[None]],
        config: Config,
        queue_size: int = 1,
    ):
        self._message_handler = message_handler
        self._message_queue = asyncio.Queue(maxsize=queue_size)
        self._config = config

    async def _message_receiver(self, websocket) -> None:
        """消息接收协程"""
        async for message in websocket:
            if self._message_queue.full():
                logger.debug("消息队列已满，丢弃旧消息")
                self._message_queue.get_nowait()
            self._message_queue.put_nowait(message)

    async def _message_processor(self) -> None:
        """消息处理协程"""
        while True:
            message = await self._message_queue.get()
            logger.debug(f"处理消息: {message[:50]}...")
            await self._message_handler(message)

    async def handle(self, websocket) -> None:
        """处理WebSocket连接"""
        logger.info(f"新连接建立: {websocket.remote_address}")
        receiver_task = asyncio.create_task(self._message_receiver(websocket))

        try:
            await self._message_processor()
        except websockets.exceptions.ConnectionClosedError:
            logger.warning("连接异常关闭")
        finally:
            logger.info(f"连接关闭: {websocket.remote_address}")
            receiver_task.cancel()
            try:
                await receiver_task
            except asyncio.CancelledError:
                pass


async def start_websocket_server(
    message_handler: Callable[[str], Awaitable[None]], config: Config
) -> None:
    """启动WebSocket服务器"""
    logger.info(f"启动WebSocket服务器: 0.0.0.0:{config.websocket_port}")
    connection = WebSocketConnection(message_handler, config)
    async with websockets.serve(
        connection.handle,
        "0.0.0.0",
        config.websocket_port,
        ping_interval=config.ping_interval,
        ping_timeout=config.ping_timeout,
    ):
        await asyncio.Future()
