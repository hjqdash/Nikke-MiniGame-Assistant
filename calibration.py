import tkinter as tk
import ctypes

# ================= 坐标微调区域 =================
# 我根据你的截图，帮你把 X 往左大幅移动了 12 像素
# 原来是 897 -> 现在改为 885
ROI_X = 893
ROI_Y = 323
ROI_W = 766
ROI_H = 1226
GRID_ROWS = 16
GRID_COLS = 10


# ===============================================

class GridCalibrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grid Calibrator")
        self.geometry(f"{ROI_W}x{ROI_H}+{ROI_X}+{ROI_Y}")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.transparent_color = "#ff00ff"
        self.configure(bg=self.transparent_color)
        self.wm_attributes("-transparentcolor", self.transparent_color)

        # 鼠标穿透
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style | 0x80000 | 0x20
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        except:
            pass

        self.canvas = tk.Canvas(self, width=ROI_W, height=ROI_H,
                                bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        # 1. 画外框 (蓝色)
        self.canvas.create_rectangle(0, 0, ROI_W - 1, ROI_H - 1, outline="blue", width=3)

        step_x = ROI_W / GRID_COLS
        step_y = ROI_H / GRID_ROWS

        # 2. 画竖线 (红色)
        for c in range(1, GRID_COLS):
            x = c * step_x
            self.canvas.create_line(x, 0, x, ROI_H, fill="red", width=1)

        # 3. 画横线 (红色)
        for r in range(1, GRID_ROWS):
            y = r * step_y
            self.canvas.create_line(0, y, ROI_W, y, fill="red", width=1)

        # 4. 在每个格子中心画个点 (帮助确认是否对准了数字中心)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cx = c * step_x + step_x / 2
                cy = r * step_y + step_y / 2
                self.canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill="yellow", outline="yellow")


if __name__ == "__main__":
    print(">>> 网格校准器启动")
    print(">>> 请观察红线是否切到了数字？黄点是否在数字正中间？")
    print(">>> 如果不对，请关闭窗口，修改代码里的 ROI_X / ROI_Y 数值。")
    app = GridCalibrator()
    app.mainloop()