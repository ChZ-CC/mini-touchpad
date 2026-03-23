# TouchPad - 手机触控板Web版

## 项目介绍

TouchPad是一个使用Web技术实现的手机触控板工具，允许你通过手机浏览器控制电脑鼠标。

### 主要功能

- 手机触摸屏幕控制电脑鼠标移动
- 点击屏幕模拟鼠标左键点击
- 跨平台支持（Windows、Mac、Linux）
- 无需安装APP，仅需浏览器访问

## 技术栈

- **后端**：Python 3.12+，使用websockets和pyautogui库
- **前端**：HTML5 + JavaScript
- **通信**：WebSocket实时通信

## 安装依赖

### 1. 克隆项目（如果没有）

```bash
git clone <项目地址>
cd touch-pad
```

### 2. 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
. .venv/bin/activate
```

### 3. 安装依赖库

```bash
# 使用uv安装依赖
uv add websockets pyautogui

# 或使用pip
pip install websockets pyautogui
```

## 运行代码

### 1. 启动服务

```bash
python main.py
```

### 2. 查看服务信息

服务启动后会显示如下信息：

```plaintext
=== 手机触控板服务已启动 ===
1. 电脑IP地址：192.168.10.240
2. 手机浏览器访问：http://你的电脑IP:9876
3. 确保手机和电脑连接同一WiFi
```

## 使用说明

### 1. 连接准备

- 确保手机和电脑连接在同一个WiFi网络下
- 手机浏览器访问服务显示的IP地址，例如：`http://192.168.10.240:9876`

### 2. 控制方式

- **移动鼠标**：在手机屏幕上滑动手指
- **点击**：在手机屏幕上轻点（相当于鼠标左键点击）

### 3. 常见问题

- **连接失败**：检查电脑和手机是否在同一WiFi网络，IP地址是否正确
- **鼠标移动不流畅**：调整代码中的`MOUSE_SPEED`参数（数值越小越灵敏）
- **点击无反应**：确保触摸事件被正确捕获，检查浏览器兼容性

## 技术实现

### 服务端

- **HTTP服务**：提供手机端Web页面（端口9876）
- **WebSocket服务**：接收手机触摸指令并控制鼠标（端口9877）
- **鼠标控制**：使用pyautogui库模拟鼠标移动和点击

### 客户端

- **触摸事件**：监听touchstart、touchmove、touchend事件
- **WebSocket连接**：实时发送触摸数据到服务端
- **响应式设计**：适配不同手机屏幕尺寸

## 项目结构

```plaintext
touch-pad/
├── main.py          # 主程序文件
├── README.md        # 项目文档
├── pyproject.toml   # 项目配置
└── .venv/           # 虚拟环境
```

## 注意事项

- 本工具仅在局域网内使用，不支持公网访问
- 确保电脑和手机网络连接稳定
- 部分浏览器可能对触摸事件处理有所不同
- 长时间使用可能会有电池消耗，建议在需要时使用

## 扩展功能（未来计划）

- 支持鼠标右键点击
- 支持滚轮操作
- 添加键盘输入功能
- 优化响应速度和稳定性

## 许可证

MIT License
