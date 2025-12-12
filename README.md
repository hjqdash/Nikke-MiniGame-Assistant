# 🎮 Nikke Mini-Game Assistant (Visual Overlay Solver)

这是一个针对《胜利女神：妮姬》(Goddess of Victory: Nikke) 中连线消除类小游戏的视觉辅助工具。

本项目不侵入游戏内存，不发送网络封包，完全基于**计算机视觉 (CV)** 和 **屏幕覆盖 (Overlay)** 技术实现。它通过实时分析游戏画面，计算最优消除路径，并在游戏窗口上绘制可视化的辅助线（绿框），帮助玩家轻松获取高分。

## ✨ 核心功能

* **⚡ 极速识别 (High-Performance OCR)**: 集成 `mss` 截图库与 `OpenCV`，实现毫秒级屏幕捕获与处理。
* **🎯 自动抗干扰 (Anti-Interference)**: 采用 HSV 亮度二值化 + 边缘遮罩 (Center-Focus Mask) 技术，完美解决背景光效干扰，精准识别数字。
* **🧠 全能算法 (Smart Solver)**:
    * 支持横向/纵向直线扫描。
    * 支持**跨越空隙** (Bridge Gaps) 连接远端数字。
    * 支持**矩形框选** (Box Selection) 消除逻辑。
* **👁️ AR 级视觉辅助**: 使用 `Tkinter` 创建鼠标穿透的透明置顶窗口，将计算结果直接“画”在游戏里，不影响鼠标操作。
* **🛠️ 开发者工具**: 内置网格校准器 (`calibration.py`) 和 模板生成器 (`tools.py`)，可适配不同分辨率。

## 🛠️ 技术栈

* **语言**: Python 3.x
* **视觉处理**: OpenCV (cv2), NumPy
* **屏幕捕获**: MSS (比 PyAutoGUI 快 10 倍)
* **GUI 渲染**: Tkinter (Win32 API 实现鼠标穿透)
* **打包工具**: PyInstaller

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.x，然后安装依赖：
```bash
pip install opencv-python numpy mss pyinstaller
