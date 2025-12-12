import cv2
import numpy as np
import os

# ================= 你的精准坐标 =================
DEFAULT_ROI = (893, 323, 766, 1226)
DEFAULT_GRID = (16, 10)


# ===============================================

def generate_templates(image_path, roi, grid_dim):
    if not os.path.exists(image_path):
        print(f"❌ 错误：找不到图片 {image_path}，请确保它是全屏截图。")
        return

    img = cv2.imread(image_path)
    output_dir = "templates_raw"
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    x_start, y_start, w_total, h_total = roi
    rows, cols = grid_dim

    x_steps = np.linspace(x_start, x_start + w_total, cols + 1)
    y_steps = np.linspace(y_start, y_start + h_total, rows + 1)

    pad = 2
    count = 0

    print("正在切割并应用【圆形遮罩 + 高阈值】滤镜...")

    for r in range(rows):
        for c in range(cols):
            x1, y1 = int(x_steps[c]), int(y_steps[r])
            x2, y2 = int(x_steps[c + 1]), int(y_steps[r + 1])

            crop = img[y1 + pad: y2 - pad, x1 + pad: x2 - pad]
            if crop.size == 0: continue

            # === 1. 转灰度 ===
            if len(crop.shape) == 3:
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            else:
                gray = crop

            # === 2. 提高阈值 (225) ===
            # 只有最亮的白色才能通过，灰色背景全部变黑
            _, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)

            # === 3. 圆形遮罩 (切掉四个角) ===
            h, w = binary.shape
            mask = np.zeros((h, w), dtype=np.uint8)
            # 画一个白色的实心圆，圆心在图中心，半径为宽度的 45%
            center = (w // 2, h // 2)
            radius = int(min(h, w) * 0.45)
            cv2.circle(mask, center, radius, 255, -1)

            # 应用遮罩：圆圈以外全部变黑
            clean = cv2.bitwise_and(binary, mask)

            # 保存
            cv2.imwrite(f"{output_dir}/{r}_{c}.png", clean)
            count += 1

    print(f"\n✅ 已生成 {count} 张图片。")
    print("👉 请检查：现在图片应该是【纯黑背景】，连角落也是黑的，只有中间数字是白的。")
    print("👉 挑选 1-9，覆盖到 templates 文件夹。")


if __name__ == "__main__":
    generate_templates("pink_screen.png", DEFAULT_ROI, DEFAULT_GRID)