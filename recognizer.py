import cv2
import numpy as np
import os
from typing import List, Dict


class GridRecognizer:
    def __init__(self, templates_dir: str = "templates"):
        self.templates: Dict[int, np.ndarray] = {}
        # 匹配阈值
        self.threshold = 0.65
        self._load_templates(templates_dir)

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        预处理：与 tools.py 保持 100% 一致
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # 1. 高阈值 (225) 过滤背景
        _, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)

        # 2. 圆形遮罩
        h, w = binary.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        center = (w // 2, h // 2)
        radius = int(min(h, w) * 0.45)
        cv2.circle(mask, center, radius, 255, -1)

        clean_binary = cv2.bitwise_and(binary, mask)
        return clean_binary

    def _load_templates(self, dir_path: str):
        if not os.path.exists(dir_path): return
        for i in range(1, 10):
            p = os.path.join(dir_path, f"{i}.png")
            if os.path.exists(p):
                raw_img = cv2.imread(p)
                if raw_img is not None:
                    self.templates[i] = self._preprocess(raw_img)
        print(f"已加载 {len(self.templates)} 个模板。")

    def identify_cell(self, cell_img: np.ndarray) -> int:
        binary_cell = self._preprocess(cell_img)

        best_score = -1.0
        best_num = 0

        for num, tmpl in self.templates.items():
            if tmpl.shape != binary_cell.shape:
                tmpl = cv2.resize(tmpl, (binary_cell.shape[1], binary_cell.shape[0]))

            res = cv2.matchTemplate(binary_cell, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > best_score:
                best_score = max_val
                best_num = num

        if best_score < self.threshold:
            return 0

        return best_num

    def process_screenshot(self, screen_np: np.ndarray, roi: tuple, rows: int, cols: int) -> List[List[int]]:
        x_start, y_start, w_total, h_total = roi

        # 浮点数切割
        x_steps = np.linspace(x_start, x_start + w_total, cols + 1)
        y_steps = np.linspace(y_start, y_start + h_total, rows + 1)

        pad = 2
        matrix = [[0] * cols for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                x1, y1 = int(x_steps[c]), int(y_steps[r])
                x2, y2 = int(x_steps[c + 1]), int(y_steps[r + 1])

                cell = screen_np[y1 + pad: y2 - pad, x1 + pad: x2 - pad]
                if cell.size == 0: continue

                matrix[r][c] = self.identify_cell(cell)

        return matrix