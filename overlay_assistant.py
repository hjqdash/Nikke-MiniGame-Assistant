import tkinter as tk
import threading
import ctypes
import numpy as np
import time
import mss
from recognizer import GridRecognizer

# ================= 你的校准坐标 =================
ROI_X, ROI_Y = 893, 323
ROI_W, ROI_H = 766, 1226
GRID_ROWS, GRID_COLS = 16, 10


# ===============================================

class GameOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nikke Assistant")
        self.geometry(f"{ROI_W}x{ROI_H}+{ROI_X}+{ROI_Y}")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.transparent_color = "#ff00ff"
        self.configure(bg=self.transparent_color)
        self.wm_attributes("-transparentcolor", self.transparent_color)
        self.make_click_through()

        self.canvas = tk.Canvas(self, width=ROI_W, height=ROI_H,
                                bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rec = GridRecognizer()
        self.monitor = {"top": ROI_Y, "left": ROI_X, "width": ROI_W, "height": ROI_H}

        self.running = True
        self.current_paths = []
        self.failed_cells = []

        self.thread = threading.Thread(target=self.calculate_loop, daemon=True)
        self.thread.start()
        self.update_ui()

    def make_click_through(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style | 0x80000 | 0x20
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        except:
            pass

    def calculate_loop(self):
        with mss.mss() as sct:
            while self.running:
                try:
                    img_bgra = np.array(sct.grab(self.monitor))
                    img_bgr = img_bgra[:, :, :3]

                    # 识别
                    matrix = self.rec.process_screenshot(
                        img_bgr, (0, 0, ROI_W, ROI_H), GRID_ROWS, GRID_COLS
                    )

                    # 标记识别失败 (仅用于调试)
                    fails = []
                    for r in range(GRID_ROWS):
                        for c in range(GRID_COLS):
                            if matrix[r][c] == 0:
                                fails.append((r, c))
                    self.failed_cells = fails

                    # === 核心算法：全能消除 ===
                    self.current_paths = self.solve_all_patterns(matrix)

                    time.sleep(0.01)
                except Exception as e:
                    time.sleep(1)

    def solve_all_patterns(self, matrix):
        """
        全能算法：
        1. 优先找横线 (1xN)
        2. 再找竖线 (Nx1)
        3. 最后找矩形框 (MxN) - [新功能]
        """
        rows, cols = len(matrix), len(matrix[0])
        paths = []
        used = set()

        # --- 阶段 1: 横向扫描 (效率最高) ---
        for r in range(rows):
            for c in range(cols):
                if matrix[r][c] == 0 or (r, c) in used: continue
                current_sum = 0
                temp_path = []
                for k in range(c, cols):
                    if (r, k) in used: break  # 遇到占位就停
                    val = matrix[r][k]
                    if val == 0:  # 跨越空地
                        temp_path.append((r, k))
                        continue

                    current_sum += val
                    temp_path.append((r, k))

                    if current_sum == 10:
                        paths.append(temp_path)
                        for pr, pc in temp_path:
                            if matrix[pr][pc] != 0: used.add((pr, pc))
                        break
                    elif current_sum > 10:
                        break

        # --- 阶段 2: 纵向扫描 ---
        for c in range(cols):
            for r in range(rows):
                if matrix[r][c] == 0 or (r, c) in used: continue
                current_sum = 0
                temp_path = []
                for k in range(r, rows):
                    if (k, c) in used: break
                    val = matrix[k][c]
                    if val == 0:
                        temp_path.append((k, c))
                        continue

                    current_sum += val
                    temp_path.append((k, c))

                    if current_sum == 10:
                        paths.append(temp_path)
                        for pr, pc in temp_path:
                            if matrix[pr][pc] != 0: used.add((pr, pc))
                        break
                    elif current_sum > 10:
                        break

        # --- 阶段 3: 矩形框选 (Box Selection) [新功能] ---
        # 扫描所有可能的矩形区域 (r1,c1) 到 (r2,c2)
        # 仅当该区域内没有被占用的格子，且总和为10时生效
        for r1 in range(rows):
            for c1 in range(cols):
                # 起点检查
                if matrix[r1][c1] == 0 or (r1, c1) in used: continue

                # 遍历终点 (r2, c2)
                # 限制：r2 >= r1, c2 >= c1
                # 且为了避免重复，我们只找 height > 1 或 width > 1 的情况
                # (因为单行单列已经被上面处理了，但为了保险起见，全扫也行)
                for r2 in range(r1, rows):
                    for c2 in range(c1, cols):
                        # 如果是单点，跳过
                        if r1 == r2 and c1 == c2: continue
                        # 如果已经算过直线了，这里可以跳过直线情况，只算矩形(r2>r1 and c2>c1)
                        # 但为了捡漏，我们还是扫一遍

                        # === 快速检查矩形区域 ===
                        rect_sum = 0
                        rect_path = []
                        valid_rect = True

                        # 遍历矩形内的每一个格子
                        for r in range(r1, r2 + 1):
                            for c in range(c1, c2 + 1):
                                if (r, c) in used:
                                    valid_rect = False
                                    break
                                val = matrix[r][c]
                                rect_sum += val
                                rect_path.append((r, c))
                            if not valid_rect: break
                            if rect_sum > 10:  # 剪枝：如果中途已经超了，就不用继续加了
                                valid_rect = False
                                break

                        if valid_rect and rect_sum == 10:
                            # 找到了一个合法的矩形！
                            paths.append(rect_path)
                            # 标记所有非0格子为已用
                            for pr, pc in rect_path:
                                if matrix[pr][pc] != 0: used.add((pr, pc))
                            # 既然这个起点找到了一个矩形，就不需要在这个起点找更大的矩形了(贪心)
                            # 跳出内层循环
                            break

                            # 如果在这个起点找到了矩形，外层循环也继续下一个起点
                    # 注意：Python跳出多层循环比较麻烦，这里简单处理不强制跳出
                    pass

        return paths

    def update_ui(self):
        self.canvas.delete("all")
        step_x = ROI_W / GRID_COLS
        step_y = ROI_H / GRID_ROWS

        # 1. 绘制虚线黄框 (空地/未知)
        # 仅当空地不属于任何有效路径时才显示，减少干扰
        if len(self.current_paths) > 0:
            active_cells = set()
            for path in self.current_paths:
                for p in path: active_cells.add(p)

            for r, c in self.failed_cells:
                if (r, c) not in active_cells:
                    x1, y1 = c * step_x, r * step_y
                    self.canvas.create_rectangle(
                        x1 + 12, y1 + 12, x1 + step_x - 12, y1 + step_y - 12,
                        outline="yellow", width=1, dash=(2, 2)
                    )

        # 2. 绘制绿框 (路径)
        for path in self.current_paths:
            if not path: continue

            # 获取矩形的左上角和右下角
            # path 里的点顺序可能是乱的 (尤其是矩形扫描时)，所以要算 min/max
            rows = [p[0] for p in path]
            cols = [p[1] for p in path]

            r_min, r_max = min(rows), max(rows)
            c_min, c_max = min(cols), max(cols)

            x1 = c_min * step_x
            y1 = r_min * step_y
            x2 = (c_max + 1) * step_x
            y2 = (r_max + 1) * step_y

            # 绘制绿色粗框
            self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, outline="#00FF00", width=4)

        self.after(30, self.update_ui)


if __name__ == "__main__":
    print(">>> 全能辅助启动：支持 直线 + 矩形框选！")
    app = GameOverlay()
    app.mainloop()