# Touchpad - 手机触控板

极简网页版触控版应用，允许用户通过移动端浏览器控制电脑鼠标。

## 功能特性

- 📱 手机浏览器作为触控板
- 🖱️ 鼠标控制（移动、点击、双击、陀螺仪控制）
- ⚡ 低延迟响应（~100ms）
- 🔒 心跳保活机制，自动重连机制
- 🎯 消息队列优化，防止积压
- 🔧 可配置的参数

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

或使用 uv（推荐使用）:

```bash
uv sync
```

### 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

### 运行程序

```bash
python main.py
```

### 使用方法

1. 确保手机和电脑连接同一WiFi
2. 查看控制台输出的IP地址
3. 在手机浏览器访问显示的URL
4. 开始使用触控板

### SSL配置（可选）

如果要使用陀螺仪功能，需要启用HTTPS/WSS加密连接：

1. 生成SSL证书：
   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
   ```
   
2. 在 `.env` 文件中启用SSL：
   ```env
   ENABLE_SSL=true
   CERT_FILE=cert.pem
   KEY_FILE=key.pem
   ```

3. 重启应用

## 配置说明

| 参数             | 说明             | 默认值   |
| ---------------- | ---------------- | -------- |
| MOUSE_SPEED      | 鼠标移动速度     | 3.0      |
| MESSAGE_INTERVAL | 消息发送间隔(ms) | 16       |
| CLICK_THRESHOLD  | 点击阈值(像素)   | 1        |
| HTTP_PORT        | HTTP服务端口     | 9876     |
| WEBSOCKET_PORT   | WebSocket端口    | 9877     |
| DEBUG_MODE       | 调试模式         | false    |
| ENABLE_SSL       | 启用SSL加密      | false    |
| CERT_FILE        | SSL证书文件路径  | cert.pem |
| KEY_FILE         | SSL私钥文件路径  | key.pem  |
| GYRO_THRESHOLD   | 陀螺仪灵敏度阈值 | 0.25     |

## 开发指南

### 添加新命令

1. 在 `touchpad/handlers/` 创建新的处理器类
2. 继承 `CommandHandler` 基类
3. 实现 `execute` 方法
4. 在 `CommandDispatcher` 中注册

示例：

```python
from touchpad.handlers.base import CommandHandler
from typing import List

class YourCommandHandler(CommandHandler):
    def execute(self, args: List[str]) -> None:
        ...
```

## 技术栈

- Python 3.7+
- asyncio - 异步编程
- websockets - WebSocket 通信
- pynput - 鼠标控制
- python-dotenv - 环境变量管理
- ssl - SSL/TLS加密
- cryptography - 证书生成

## 性能优化

- 使用单元素消息队列防止积压
- 只处理最新消息，丢弃积压消息
- 异步处理提高并发
- 心跳机制保证连接稳定

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 更新日志

### v1.2.0 (2026-05-14)

- ✨ 新增陀螺仪控制功能（手机倾斜控制鼠标）
- 📶 新增连接状态指示器
- 📱 优化移动端UI和体验
- 🐛 修复Windows文件锁定问题
- 🚀 优化WebSocket连接管理

### v1.1.0 (2026-03-25)

- 重构项目结构
- 添加日志系统
- 优化消息处理
- 改进代码质量
- 完善文档

### v1.0.0

- 初始版本
- 基本触控板功能