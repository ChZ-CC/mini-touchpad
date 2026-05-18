"""HTTP/HTTPS服务器

提供HTTP/HTTPS服务，用于提供前端页面。
"""

import ssl
from http.server import HTTPServer as StdlibHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Optional
from touchpad.log import get_logger
from touchpad.utils import get_local_ip

logger = get_logger(__name__)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器

    处理HTTP GET请求，返回HTML页面。
    """

    def __init__(self, *args, **kwargs):
        self._html_content = prepare_html(load_html_content())
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self._html_content.encode("utf-8"))

    def log_message(self, format, *args):
        """禁用默认日志"""
        logger.info(f"{format % args} - {self.client_address[0]} - {self.path}")


class HTTPServer:
    """HTTP/HTTPS服务器

    提供HTTP/HTTPS服务，用于提供前端页面。
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9876,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        self._host = host
        self._port = port
        self._server: Optional[StdlibHTTPServer] = None
        self._thread: Optional[Thread] = None
        self._ssl_context = ssl_context

    def start(self) -> str:
        """启动HTTP/HTTPS服务器"""
        ip = f"{self._host}:{self._port}"
        logger.info(f"[start] starting http server, listening on {ip}...")
        self._server = StdlibHTTPServer((self._host, self._port), HTTPRequestHandler)

        if self._ssl_context:
            self._server.socket = self._ssl_context.wrap_socket(
                self._server.socket, server_side=True
            )

        self._thread = Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()
        logger.info("[start] http server started")
        local_ip = f"{get_local_ip()}:{self._port}"  # 获取本地IP地址
        return f"https://{local_ip}" if self._ssl_context else f"http://{local_ip}"

    def stop(self) -> None:
        """停止HTTP服务器"""
        logger.info("[stop] stopping http server...")
        if self._server:
            self._server.shutdown()
            if self._thread:
                self._thread.join()

        logger.info("[stop] http server stopped")


def load_html_content(file_path: str = "static/touchpad.html") -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def prepare_html(html_content: str) -> str:
    from touchpad.config import config

    replacements = {
        "const CLICK_THRESHOLD = 10;": f"const CLICK_THRESHOLD = {config.click_threshold};",
        "const MESSAGE_INTERVAL = 16;": f"const MESSAGE_INTERVAL = {config.message_interval};",
        "const WEBSOCKET_PORT = 9877;": f"const WEBSOCKET_PORT = {config.websocket_port};",
        "const DEBUG_MODE = false;": f"const DEBUG_MODE = {'true' if config.debug_mode else 'false'}",
    }
    for old, new in replacements.items():
        html_content = html_content.replace(old, new)
    return html_content
