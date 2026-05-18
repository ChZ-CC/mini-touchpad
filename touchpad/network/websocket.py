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
            if message == "ping":
                logger.debug(f"收到心跳: from {websocket.remote_address}")
                continue
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
            logger.info(f"[handle] 连接异常关闭: {websocket.remote_address}")
        except (ConnectionResetError, OSError) as e:
            logger.info(f"[handle] 网络异常: {e}")
        except Exception as e:
            logger.error(f"[handle] 未处理的异常: {type(e).__name__}: {e}")
        finally:
            logger.info(
                f"[handle] canceling receive_task for {websocket.remote_address}"
            )
            receiver_task.cancel()
            try:
                await receiver_task
            except websockets.exceptions.ConnectionClosedError as e:
                logger.info(f"[handle] receive_task 连接异常关闭, 错误: {e}")
            except asyncio.CancelledError:
                pass
            logger.info(f"[handle] 连接已关闭: {websocket.remote_address}")


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
        self._stop_event = None  # 用于通知服务器停止的事件
        self._wss = set()  # 跟踪所有活动连接
        self.conn = WebSocketConnection(self._message_handler, self._config)

    async def _handle_connection(self, websocket):
        """处理单个WebSocket连接"""
        self._wss.add(websocket)

        try:
            await self.conn.handle(websocket)
        finally:
            self._wss.discard(websocket)

    async def start(self) -> None:
        """启动WebSocket服务器"""
        logger.info(
            f"[start] starting websocket server, listening on 0.0.0.0:{self._config.websocket_port}..."
        )

        if self._ssl_context:
            logger.info("[start] ssl enabled, starting WSS server...")
            self._server = await websockets.serve(
                self._handle_connection,
                "0.0.0.0",
                self._config.websocket_port,
                ping_interval=self._config.ping_interval,
                ping_timeout=self._config.ping_timeout,
                ssl=self._ssl_context,  # 启用 SSL
            )
        else:
            logger.info("[start] ssl disabled, starting WebSocket server...")
            self._server = await websockets.serve(
                self._handle_connection,
                "0.0.0.0",
                self._config.websocket_port,
                ping_interval=self._config.ping_interval,
                ping_timeout=self._config.ping_timeout,
            )

        self._serve_task = asyncio.create_task(self._server.serve_forever())
        logger.info("[start] serve_forever task created")
        self._stop_event = asyncio.Event()  # 创建停止事件
        logger.info("[start] stop event created")

        try:
            # 等待停止事件被设置
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.debug("[start] cancelled while waiting for stop event")
        # finally:
        #     logger.debug("[start] cleanup...")
        #     await self.cleanup()

    async def close(self) -> None:
        """主动关闭WebSocket服务器"""
        logger.info("[close] closing websocket server...")

        # 设置停止事件
        if self._stop_event:
            logger.info("[close] sending stop signal to server...")
            self._stop_event.set()
            await self.cleanup()

        logger.info("[close] websocket server closed")

    async def cleanup(self) -> None:
        """关闭WebSocket服务器"""
        # 优雅地关闭所有客户端连接
        if self._wss:
            logger.debug(f"[cleanup] closing {len(self._wss)} client connections...")
            close_tasks = [
                asyncio.create_task(ws.close(code=1000, reason="Server shutting down"))
                for ws in list(self._wss)
            ]
            if close_tasks:
                try:
                    await asyncio.wait_for(asyncio.gather(*close_tasks), timeout=3)
                except asyncio.TimeoutError:
                    logger.warning("[cleanup] 部分连接关闭超时")
                except Exception as e:
                    logger.debug(f"[cleanup] 关闭连接时出错: {e}")
        self._wss.clear()

        # 取消服务任务
        if self._serve_task:
            logger.info(f"[cleanup] cancelling server_task...")
            self._serve_task.cancel()
            try:
                await asyncio.wait_for(self._serve_task, timeout=2)
            except asyncio.CancelledError:
                logger.info("[cleanup] server_task cancelled")
            except asyncio.TimeoutError:
                logger.info(
                    f"[cleanup] timeout while cancelling server_task. cancelled={self._serve_task.cancelled()}"
                )

        # 关闭服务器
        if self._server:
            logger.debug("[cleanup] closing server")
            self._server.close()
            try:
                await asyncio.wait_for(self._server.wait_closed(), timeout=2)
            except asyncio.TimeoutError:
                logger.info("[cleanup] server close timeout")

            self._server = None
            self._serve_task = None
            self._wss.clear()

        logger.info("[cleanup] websocket server cleanup complete")


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
