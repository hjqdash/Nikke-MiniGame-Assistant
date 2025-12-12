# 🎮 Nikke Mini-Game Assistant (Visual Overlay Solver)

这是一个针对《胜利女神：妮姬》(Goddess of Victory: Nikke) 中连线消除类小游戏的视觉辅助工具。

本项目**不侵入游戏内存**，**不发送网络封包**，完全基于 **计算机视觉 (CV)** 和 **屏幕覆盖 (Overlay)** 技术实现。它通过实时分析游戏画面，计算最优消除路径，并在游戏窗口上绘制可视化的辅助线（绿框），帮助玩家轻松获取高分。

---

## ✨ 核心功能

* **⚡ 极速识别 (High-Performance OCR)**
    * 集成 `mss` 截图库与 `OpenCV`，实现毫秒级屏幕捕获与处理。
* **🎯 自动抗干扰 (Anti-Interference)**
    * 采用 HSV 亮度二值化 + 边缘遮罩 (Center-Focus Mask) 技术，完美解决背景光效干扰，精准识别数字。
* **🧠 全能算法 (Smart Solver)**
    * 支持横向/纵向直线扫描。
    * 支持 **跨越空隙 (Bridge Gaps)** 连接远端数字。
    * 支持 **矩形框选 (Box Selection)** 消除逻辑。
* **👁️ AR 级视觉辅助**
    * 使用 `Tkinter` 创建鼠标穿透的透明置顶窗口，将计算结果直接“画”在游戏里，不影响鼠标操作。
* **🛠️ 开发者工具**
    * 内置网格校准器 (`calibration.py`) 和 模板生成器 (`tools.py`)，可适配不同分辨率。

## 🛠️ 技术栈

* **语言**: Python 3.x
* **视觉处理**: OpenCV (cv2), NumPy
* **屏幕捕获**: MSS (比 PyAutoGUI 快 10 倍)
* **GUI 渲染**: Tkinter (Win32 API 实现

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.x，然后安装项目依赖：

```bash
pip install pip install -r requirements.txt
```

### 2. 校准坐标 (首次运行必须)
由于不同电脑的分辨率不同，请先运行校准工具：

```bash
python calibration.py
```

* **观察**: 检查红色网格是否完美覆盖游戏中的方格。
* **调整**: 如果未对齐，请修改代码中的 `ROI_X`, `ROI_Y` 等参数直到重合。

### 3. 生成模板
截取一张游戏全屏图（命名为 `pink.png`），然后运行：

```bash
python tools.py
```

程序会自动切割并处理出纯黑底白字的数字模板。请人工挑选最清晰的 1-9 图片，放入 `templates` 文件夹中。

### 4. 启动辅助
进入小游戏界面，运行：

```bash
python overlay_assistant.py
```

* **🟩 绿框**: 表示算法计算出的最优消除路径。
* **🟨 黄框 (虚线)**: 表示无法识别或空地区域。

## 📂 项目结构

```text
.
├── overlay_assistant.py  # [主程序] 透明覆盖层与核心逻辑
├── recognizer.py         # [核心] 图像识别与抗干扰算法
├── tools.py              # [工具] 自动切图与模板生成
├── calibration.py        # [工具] 可视化坐标校准器
├── templates/            # [资源] 数字模板图片文件夹
└── README.md             # 项目说明文档
```

## ⚠️ 免责声明

> **本工具仅供学习与技术研究使用（计算机视觉算法验证）。**
>
> 请勿将本工具用于商业用途，或在违反游戏服务条款的情况下使用。开发者不对因使用本工具导致的账号封禁或其他风险负责。请合理使用。

---

