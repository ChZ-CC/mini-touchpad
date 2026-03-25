# Touchpad - 手机触控板

一个基于WebSocket的手机触控板应用，允许用户通过手机浏览器控制电脑鼠标。

## 功能特性

- 📱 手机浏览器作为触控板
- 🖱️ 完整的鼠标控制（移动、点击、拖拽）
- ⚡ 低延迟响应（~100ms）
- 🔒 心跳保活机制
- 🎯 消息队列优化，防止积压
- 🔧 可配置的参数
- 📊 可选的调试模式

## 项目结构

```
touch-pad/
├── touchpad/              # 主包
│   ├── __init__.py        # 包初始化
│   ├── app.py             # 应用主类
│   ├── config.py          # 配置管理
│   ├── log.py             # 日志系统
│   ├── utils.py           # 工具函数
│   ├── handlers/          # 命令处理器
│   │   ├── __init__.py
│   │   ├── base.py        # 基类
│   │   ├── mouse.py       # 鼠标命令
│   │   └── dispatcher.py  # 命令分发
│   └── network/           # 网络模块
│       ├── __init__.py
│       ├── http.py        # HTTP服务器
│       └── websocket.py   # WebSocket服务器
├── static/                # 静态文件
│   └── touchpad.html     # 前端页面
├── logs/                  # 日志目录
├── docs/                  # 文档目录
├── main.py               # 程序入口
├── requirements.txt       # 依赖列表
├── .env                  # 环境变量
├── .env.example          # 环境变量示例
└── README.md            # 本文件
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

或使用 uv:

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

## 配置说明

| 参数             | 说明             | 默认值 |
| ---------------- | ---------------- | ------ |
| MOUSE_SPEED      | 鼠标移动速度     | 3.0    |
| MESSAGE_INTERVAL | 消息发送间隔(ms) | 16     |
| CLICK_THRESHOLD  | 点击阈值(像素)   | 1      |
| HTTP_PORT        | HTTP服务端口     | 9876   |
| WEBSOCKET_PORT   | WebSocket端口    | 9877   |
| DEBUG_MODE       | 调试模式         | false  |

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

class ScrollCommandHandler(CommandHandler):
    def execute(self, args: List[str]) -> None:
        if len(args) == 1:
            clicks = int(args[0])
            pyautogui.scroll(clicks)
```

## 技术栈

- Python 3.7+
- asyncio - 异步编程
- websockets - WebSocket 通信
- pyautogui - 鼠标控制
- python-dotenv - 环境变量管理

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

### v1.1.0 (2026-03-25)

- 重构项目结构
- 添加日志系统
- 优化消息处理
- 改进代码质量
- 完善文档

### v1.0.0

- 初始版本
- 基本触控板功能
