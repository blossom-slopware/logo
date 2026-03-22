import subprocess
import sys
import math
import re


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
    花朵绝对大小不变，画布缩小到 canvas_size * scale
    画布中心对准花朵包围盒中心
    """
    # 计算花朵包围盒中心（在 SVG 坐标系中，原点在 SVG 中心）
    min_x, min_y, max_x, max_y = get_flower_bbox()
    flower_center_x = (min_x + max_x) / 2
    flower_center_y = (min_y + max_y) / 2

    print(f"花朵包围盒: ({min_x:.1f}, {min_y:.1f}) - ({max_x:.1f}, {max_y:.1f})")
    print(f"花朵中心: ({flower_center_x:.1f}, {flower_center_y:.1f})")

    # 输出画布尺寸（像素）
    output_size = int(canvas_size * scale)

    # viewBox 尺寸：画布对应的 SVG 坐标系大小
    # 原来是 800x800，现在缩小到 800 * scale
    viewbox_size = svg_width * scale
    viewbox_x = (svg_width / 2) + flower_center_x - viewbox_size / 2
    viewbox_y = (svg_height / 2) + flower_center_y - viewbox_size / 2

    print(f"输出尺寸: {output_size}x{output_size}")
    print(f"viewBox: {viewbox_x:.1f} {viewbox_y:.1f} {viewbox_size:.1f} {viewbox_size:.1f}")

    # 读取原始 SVG
    with open(svg_path, "r") as f:
        svg_content = f.read()

    # 修改 viewBox 和 width/height
    # 移除现有的 width 和 height 属性
    svg_content = re.sub(r'\swidth="[^"]*"', "", svg_content)
    svg_content = re.sub(r'\sheight="[^"]*"', "", svg_content)

    # 添加新的 width、height 和 viewBox
    new_attrs = f' width="{output_size}" height="{output_size}" viewBox="{viewbox_x:.2f} {viewbox_y:.2f} {viewbox_size:.2f} {viewbox_size:.2f}"'
    svg_content = svg_content.replace("<svg ", f"<svg{new_attrs} ")

    # 写入临时 SVG
    temp_svg = "/tmp/temp_flower.svg"
    with open(temp_svg, "w") as f:
        f.write(svg_content)

    # 使用 rsvg-convert 转换为 PNG
    result = subprocess.run(
        [
            "rsvg-convert",
            "--format",
            "png",
            "-o",
            png_path,
            temp_svg,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"转换失败: {result.stderr}")
        sys.exit(1)

    print(f"已生成: {png_path} ({output_size}x{output_size})")


if __name__ == "__main__":
    svg_to_png("flower_masked_rounded.svg", "flower_masked_rounded.png", canvas_size=4096, scale=0.46)
