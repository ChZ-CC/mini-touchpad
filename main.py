import asyncio
from datetime import datetime
import websockets
import pyautogui
import os
import dotenv

# 指令常量
CMD_MOVE = "move"
CMD_LEFT_DOWN = "left_down"
CMD_LEFT_UP = "left_up"
CMD_RIGHT_DOWN = "right_down"
CMD_RIGHT_UP = "right_up"

# 禁用PyAutoGUI的防误触保护（加快响应）
pyautogui.FAILSAFE = False

# 读取配置参数（从环境变量或使用默认值）
dotenv.load_dotenv()
MOUSE_SPEED = float(os.getenv("MOUSE_SPEED", "3.0"))
MESSAGE_INTERVAL = int(os.getenv("MESSAGE_INTERVAL", "16"))
CLICK_THRESHOLD = int(os.getenv("CLICK_THRESHOLD", "1"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "9876"))
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "9877"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false") in ["True", "true", "1", "t"]

# 读取前端HTML文件
with open("touchpad.html", "r", encoding="utf-8") as f:
    HTML_PAGE = f.read()

# 替换前端HTML中的配置参数
HTML_PAGE = HTML_PAGE.replace(
    "const MOUSE_SPEED = 3.0;", f"const MOUSE_SPEED = {MOUSE_SPEED};"
)
HTML_PAGE = HTML_PAGE.replace(
    "const CLICK_THRESHOLD = 10;", f"const CLICK_THRESHOLD = {CLICK_THRESHOLD};"
)
HTML_PAGE = HTML_PAGE.replace(
    "const MESSAGE_INTERVAL = 16;", f"const MESSAGE_INTERVAL = {MESSAGE_INTERVAL};"
)
HTML_PAGE = HTML_PAGE.replace(
    "const WEBSOCKET_PORT = 9877;", f"const WEBSOCKET_PORT = {WEBSOCKET_PORT};"
)
HTML_PAGE = HTML_PAGE.replace(
    "const DEBUG_MODE = false;",
    f"const DEBUG_MODE = {'true' if DEBUG_MODE else 'false'}",
)

# 心跳超时时间（如 30 秒）
PING_INTERVAL = 30
PING_TIMEOUT = 10


# 启动心跳任务
async def ping_keep_alive(websocket):
    try:
        while True:
            await asyncio.sleep(PING_INTERVAL)
            # 发送 ping 帧（websockets 库自动处理）
            await websocket.ping()
            # 等待 pong 响应，超时则断开
            await asyncio.wait_for(websocket.ensure_open(), timeout=PING_TIMEOUT)
    except asyncio.TimeoutError:
        print("心跳超时，关闭连接")
        await websocket.close(code=1000, reason="ping timeout")


# 处理WebSocket消息的核心函数
async def handle_message(websocket):
    # 启动心跳任务
    ping_task = asyncio.create_task(ping_keep_alive(websocket))
    try:
        # 使用队列来缓冲消息，避免阻塞接收
        message_queue = asyncio.Queue(maxsize=1)

        async def message_receiver():
            async for message in websocket:
                try:
                    # 非阻塞方式放入队列，如果队列满则丢弃旧消息
                    message_queue.put_nowait(message)
                except asyncio.QueueFull:
                    # 队列已满，取出旧消息放入新消息
                    try:
                        message_queue.get_nowait()
                        message_queue.put_nowait(message)
                    except:
                        pass

        # 启动消息接收协程
        asyncio.create_task(message_receiver())

        # 处理消息
        while True:
            message = await message_queue.get()
            now = datetime.now()
            if DEBUG_MODE:
                print(f"收到消息[{now}]: {message}")
            parts = message.split("|")
            cmd = parts[0]
            args = parts[1].split(",") if len(parts) > 1 else []

            if cmd == CMD_MOVE and len(args) == 2:
                # 移动鼠标（相对当前位置）
                dx = float(args[0])
                dy = float(args[1])
                pyautogui.moveRel(dx, dy, duration=0)
            elif cmd == CMD_LEFT_DOWN:
                # 鼠标左键按下
                pyautogui.mouseDown(button="left")
            elif cmd == CMD_LEFT_UP:
                # 鼠标左键抬起
                pyautogui.mouseUp(button="left")
            elif cmd == CMD_RIGHT_DOWN:
                # 鼠标右键按下
                pyautogui.mouseDown(button="right")
            elif cmd == CMD_RIGHT_UP:
                # 鼠标右键抬起
                pyautogui.mouseUp(button="right")
            else:
                print(f"未知指令：{message}")
            if DEBUG_MODE:
                print(f"耗时：{datetime.now() - now}")
    except websockets.exceptions.ConnectionClosedError:
        print("连接异常关闭")
    finally:
        # 取消心跳任务
        ping_task.cancel()
        try:
            await ping_task
        except asyncio.CancelledError:
            pass


# 启动WebSocket服务 + HTTP静态页面服务
async def main():
    # 启动WebSocket服务（监听所有网卡）
    if DEBUG_MODE:
        print(
            f"当前配置：\n\tMOUSE_SPEED={MOUSE_SPEED}"
            f"\n\tMESSAGE_INTERVAL={MESSAGE_INTERVAL}"
            f"\n\tCLICK_THRESHOLD={CLICK_THRESHOLD}"
            f"\n\tHTTP_PORT={HTTP_PORT}"
            f"\n\tWEBSOCKET_PORT={WEBSOCKET_PORT}"
            f"\n\tDEBUG_MODE={DEBUG_MODE}"
        )
    async with websockets.serve(handle_message, "0.0.0.0", WEBSOCKET_PORT):
        ip = get_local_ip()
        print("=== 手机触控板服务已启动 ===")
        print(f"1. 电脑IP地址：{ip}")
        print(f"2. 手机浏览器访问：http://{ip}:{HTTP_PORT}")
        print("3. 确保手机和电脑连接同一WiFi")
        await asyncio.Future()  # 保持服务运行


# 获取电脑本地IP（方便用户填写）
def get_local_ip():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# 启动HTTP服务（用于提供手机端Web页面）
from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))


# 同时启动WebSocket和HTTP服务
if __name__ == "__main__":
    import threading

    # 启动HTTP服务
    http_server = HTTPServer(("0.0.0.0", HTTP_PORT), SimpleHTTPRequestHandler)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.daemon = True
    http_thread.start()

    # 启动WebSocket服务
    asyncio.run(main())
