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


def svg_to_png(svg_path, png_path, size=4096):
    """将 SVG 转换为透明背景的 PNG，并以花朵包围盒中心为基准裁剪 40% 区域"""
    # 计算花朵包围盒中心（在 SVG 坐标系中，原点在 SVG 中心）
    min_x, min_y, max_x, max_y = get_flower_bbox()
    flower_center_x = (min_x + max_x) / 2
    flower_center_y = (min_y + max_y) / 2

    print(f"花朵包围盒: ({min_x:.1f}, {min_y:.1f}) - ({max_x:.1f}, {max_y:.1f})")
    print(f"花朵中心: ({flower_center_x:.1f}, {flower_center_y:.1f})")

    # 先生成较大的临时图像
    temp_png = "/tmp/temp_flower.png"
    result = subprocess.run(
        [
            "rsvg-convert",
            "-w",
            str(size),
            "-h",
            str(size),
            "--keep-aspect-ratio",
            "--format",
            "png",
            "-o",
            temp_png,
            svg_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"转换失败: {result.stderr}")
        sys.exit(1)

    # 计算裁剪参数
    crop_size = int(size * 0.4)

    # 将花朵中心从 SVG 坐标系（原点在中心）转换到图像坐标系（原点在左上角）
    # SVG 中心在图像中的位置
    img_center_x = size / 2
    img_center_y = size / 2

    # 花朵中心在图像中的位置（SVG 坐标系 y 轴向下，需要调整）
    flower_img_x = img_center_x + flower_center_x * (size / svg_width)
    flower_img_y = img_center_y + flower_center_y * (size / svg_height)

    # 裁剪区域的左上角偏移
    offset_x = int(flower_img_x - crop_size / 2)
    offset_y = int(flower_img_y - crop_size / 2)

    print(f"裁剪区域: {crop_size}x{crop_size} at ({offset_x}, {offset_y})")

    # 使用 ImageMagick 裁剪中心区域
    result = subprocess.run(
        [
            "convert",
            temp_png,
            "-crop",
            f"{crop_size}x{crop_size}+{offset_x}+{offset_y}",
            "+repage",
            png_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"裁剪失败: {result.stderr}")
        sys.exit(1)

    print(f"已生成: {png_path} ({crop_size}x{crop_size})")


if __name__ == "__main__":
    svg_to_png("flower_masked.svg", "flower_masked.png", size=4096)
