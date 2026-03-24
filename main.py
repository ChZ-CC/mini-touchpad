import asyncio
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
MOUSE_SPEED = float(os.getenv("MOUSE_SPEED", "3.0"))
MESSAGE_INTERVAL = int(os.getenv("MESSAGE_INTERVAL", "16"))
CLICK_THRESHOLD = int(os.getenv("CLICK_THRESHOLD", "1"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "9876"))
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "9877"))

# 读取前端HTML文件
with open("touchpad.html", "r", encoding="utf-8") as f:
    HTML_PAGE = f.read()

# 替换前端HTML中的配置参数
HTML_PAGE = HTML_PAGE.replace('"mouse_speed": 3.0', f'"mouse_speed": {MOUSE_SPEED}')
HTML_PAGE = HTML_PAGE.replace(
    '"click_threshold": 1', f'"click_threshold": {CLICK_THRESHOLD}'
)
HTML_PAGE = HTML_PAGE.replace(
    '"message_interval": 16', f'"message_interval": {MESSAGE_INTERVAL}'
)
HTML_PAGE = HTML_PAGE.replace(
    '"websocket_port": 9877', f'"websocket_port": {WEBSOCKET_PORT}'
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
        async for message in websocket:
            # 解析手机发来的字符串指令
            try:
                if message == "ping":
                    # 处理心跳消息
                    await websocket.send("pong")
                    return

                # 解析指令格式：cmd:arg1,arg2
                parts = message.split(":")
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
            except Exception as e:
                print(f"解析指令出错：{e}")
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
    print(
        f"当前配置：\n\tMOUSE_SPEED={MOUSE_SPEED}"
        f"\n\tMESSAGE_INTERVAL={MESSAGE_INTERVAL}"
        f"\n\tCLICK_THRESHOLD={CLICK_THRESHOLD}"
        f"\n\tHTTP_PORT={HTTP_PORT}"
        f"\n\tWEBSOCKET_PORT={WEBSOCKET_PORT}"
    )
    async with websockets.serve(handle_message, "0.0.0.0", WEBSOCKET_PORT):
        print("=== 手机触控板服务已启动 ===")
        print(f"1. 电脑IP地址：{get_local_ip()}")
        print(f"2. 手机浏览器访问：http://你的电脑IP:{HTTP_PORT}")
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
