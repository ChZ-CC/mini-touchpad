"""WebSocket服务器

提供WebSocket连接管理和消息处理功能。
"""

import asyncio
import http
import ssl
import websockets
from typing import Callable, Awaitable, Optional
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
            logger.debug(f"[handle] 连接异常关闭: {websocket.remote_address}")
        except (ConnectionResetError, OSError) as e:
            # 处理网络异常（如WinError 64：指定的网络名不再可用）
            logger.debug(f"[handle] 网络异常: {e}")
        except Exception as e:
            logger.error(f"[handle] 未处理的异常: {type(e).__name__}: {e}")
        finally:
            logger.debug(f"[handle] 清理连接资源: {websocket.remote_address}")
            receiver_task.cancel()
            try:
                await receiver_task
            except asyncio.CancelledError:
                pass
            logger.debug(f"[handle] 连接已关闭: {websocket.remote_address}")


class WebSocketServer:
    """WebSocket服务器

    管理多个WebSocket连接的生命周期。
    """

    def __init__(
        self,
        config: Config,
        message_handler: Callable[[str], Awaitable[None]],
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        self._config = config
        self._message_handler = message_handler
        self._server = None
        self._serve_task = None
        self._ssl_context = ssl_context

    async def start(self) -> None:
        """启动WebSocket服务器"""
        logger.info(f"启动WebSocket服务器: 0.0.0.0:{self._config.websocket_port}")
        connection = WebSocketConnection(self._message_handler, self._config)

        if self._ssl_context:
            logger.info("使用 SSL 上下文启动 WSS 服务器")
            self._server = await websockets.serve(
                connection.handle,
                "0.0.0.0",
                self._config.websocket_port,
                ping_interval=self._config.ping_interval,
                ping_timeout=self._config.ping_timeout,
                ssl=self._ssl_context,  # 启用 SSL
            )
        else:
            logger.info("启动普通 WebSocket 服务器")
            self._server = await websockets.serve(
                connection.handle,
                "0.0.0.0",
                self._config.websocket_port,
                ping_interval=self._config.ping_interval,
                ping_timeout=self._config.ping_timeout,
            )

        self._serve_task = asyncio.create_task(self._server.serve_forever())
        stop = asyncio.get_running_loop().create_future()
        try:
            await stop
        except asyncio.CancelledError:
            logger.debug("[server] WebSocket服务器已关闭")
        finally:
            logger.debug("start cleanup...")
            await self.cleanup()

    async def cleanup(self) -> None:
        """关闭WebSocket服务器"""
        if self._serve_task:
            logger.debug(f"[cleanup] cancelling server_task...")
            self._serve_task.cancel()
            try:
                logger.debug(f"[cleanup] waitting server_task")
                await asyncio.wait_for(self._serve_task, timeout=2)
            except asyncio.CancelledError:
                logger.info("[cleanup] server_task cancelled")
            except asyncio.TimeoutError:
                logger.info(
                    f"[cleanup] server_task timeout. cancelled={self._serve_task.cancelled()}"
                )

        if self._server:
            logger.debug("[cleanup] closing server")
            self._server.close()
            try:
                await asyncio.wait_for(self._server.wait_closed(), timeout=2)
            except asyncio.TimeoutError:
                logger.info("[cleanup] server close timeout")
                pass
            self._server = None
            self._serve_task = None


def health_check(connection, request):
    if request.path == "/healthz":
        return connection.respond(http.HTTPStatus.OK, "OK\n")


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
        process_request=health_check,
        ping_interval=config.ping_interval,
        ping_timeout=config.ping_timeout,
    ) as server:
        await server.serve_forever()
