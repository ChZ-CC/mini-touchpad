import asyncio
import websockets
import pyautogui
import os
import dotenv

dotenv.load_dotenv()
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


# 处理WebSocket消息的核心函数
async def handle_message(websocket):
    try:
        async for message in websocket:
            try:
                # 解析手机发来的JSON指令
                data = eval(message)  # 简化处理，生产环境建议用json.loads
                if data["type"] == "move":
                    # 移动鼠标（相对当前位置）
                    pyautogui.moveRel(data["dx"], data["dy"], duration=0)
                elif data["type"] == "left_down":
                    # 鼠标左键按下
                    pyautogui.mouseDown(button="left")
                elif data["type"] == "left_up":
                    # 鼠标左键抬起
                    pyautogui.mouseUp(button="left")
                elif data["type"] == "right_down":
                    # 鼠标右键按下
                    pyautogui.mouseDown(button="right")
                elif data["type"] == "right_up":
                    # 鼠标右键抬起
                    pyautogui.mouseUp(button="right")
            except Exception as e:
                print(f"处理指令出错：{e}")
    except Exception as e:
        # 忽略连接断开错误，避免控制台被错误信息刷屏
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
