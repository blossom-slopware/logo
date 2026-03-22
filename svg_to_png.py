import subprocess
import sys
import math


# 从 flower_masked.py 复制的几何参数
r = 100
d = r * math.sqrt(2)
intersection_y = math.sqrt(r**2 - (d / 2) ** 2)
p1_y = intersection_y
p2_y = -intersection_y
petal_tip_distance = p1_y
angles = [20, 70, 110, 160]
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2


def rotate_translate(x, y, angle_deg):
    """将花瓣本地坐标旋转并平移到花朵坐标系"""
    rotation = angle_deg + 90
    rot_rad = math.radians(rotation)
    rx = x * math.cos(rot_rad) - y * math.sin(rot_rad)
    ry = x * math.sin(rot_rad) + y * math.cos(rot_rad)
    angle_rad = math.radians(angle_deg)
    offset_x = -petal_tip_distance * math.cos(angle_rad)
    offset_y = -petal_tip_distance * math.sin(angle_rad)
    return rx + offset_x, ry + offset_y


def get_flower_bbox():
    """计算花朵的包围盒，返回 (min_x, min_y, max_x, max_y)"""
    points = []
    for angle in angles:
        # 花瓣的起点和终点
        start = rotate_translate(0, p2_y, angle)
        end = rotate_translate(0, p1_y, angle)
        points.append(start)
        points.append(end)
        # 花瓣圆弧的中点（近似）
        mid_angle = math.radians(angle + 90)
        mid_x = r * math.cos(mid_angle)
        mid_y = r * math.sin(mid_angle)
        mid = rotate_translate(mid_x, mid_y, angle)
        points.append(mid)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def svg_to_png(svg_path, png_path, canvas_size=4096, scale=0.4):
    """
    将 SVG 转换为透明背景的 PNG
    画布以花朵包围盒中心为中心，边长为 canvas_size * scale
    """
    # 计算花朵包围盒中心（在 SVG 坐标系中，原点在 SVG 中心）
    min_x, min_y, max_x, max_y = get_flower_bbox()
    flower_center_x = (min_x + max_x) / 2
    flower_center_y = (min_y + max_y) / 2

    print(f"花朵包围盒: ({min_x:.1f}, {min_y:.1f}) - ({max_x:.1f}, {max_y:.1f})")
    print(f"花朵中心: ({flower_center_x:.1f}, {flower_center_y:.1f})")

    # 输出画布尺寸
    output_size = int(canvas_size * scale)

    # 计算 viewBox：以花朵中心为中心，边长为 svg_width / scale
    # 这样放大后花朵占据画布的 scale 比例
    viewbox_size = svg_width / scale
    viewbox_x = (svg_width / 2) + flower_center_x - viewbox_size / 2
    viewbox_y = (svg_height / 2) + flower_center_y - viewbox_size / 2

    print(f"输出尺寸: {output_size}x{output_size}")
    print(f"viewBox: {viewbox_x:.1f} {viewbox_y:.1f} {viewbox_size:.1f} {viewbox_size:.1f}")

    # 使用 rsvg-convert 直接生成指定区域的 PNG
    result = subprocess.run(
        [
            "rsvg-convert",
            "-w",
            str(output_size),
            "-h",
            str(output_size),
            "--format",
            "png",
            "--page-x",
            str(viewbox_x),
            "--page-y",
            str(viewbox_y),
            "--page-width",
            str(viewbox_size),
            "--page-height",
            str(viewbox_size),
            "-o",
            png_path,
            svg_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"转换失败: {result.stderr}")
        sys.exit(1)

    print(f"已生成: {png_path} ({output_size}x{output_size})")


if __name__ == "__main__":
    svg_to_png("flower_masked_rounded.svg", "flower_masked.png", canvas_size=4096, scale=0.4)
