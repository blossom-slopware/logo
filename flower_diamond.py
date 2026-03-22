import math
import colorsys

# ==================== 用户自定义颜色 ====================
start_hex = "#ffbfcd"
end_hex = "#ff99af"

# ======================================================

# 两个等圆的参数
r = 100  # 圆的半径
d = r * math.sqrt(2)  # 圆心距离

# 计算交点
intersection_y = math.sqrt(r**2 - (d / 2) ** 2)
p1_y = intersection_y  # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）
petal_tip_distance = p1_y

# 菱形侧边顶点的 x 坐标 - 收窄为高度的约 1/4
# 花瓣高度 = p1_y - p2_y = 2 * p1_y ≈ 141.4
# 设置宽度为高度的 0.25 倍
side_x = p1_y * 0.6  # 约 17.7

# 菱形侧边顶点的 y 坐标（在中心线上，即 y=0）
side_y = 0

# 遮罩膨胀参数
diameter = 2 * r
delta = diameter / 10
r_mask = r + delta
# 遮罩的侧边顶点（膨胀后）
mask_side_x = d / 2  # 遮罩圆心不变，x 坐标相同
mask_side_y = math.sqrt(r_mask**2 - (d / 2) ** 2) - intersection_y

angles = [20, 70, 110, 160]
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2


def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip("#")
    r_val = int(hex_color[0:2], 16) / 255.0
    g_val = int(hex_color[2:4], 16) / 255.0
    b_val = int(hex_color[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r_val, g_val, b_val)
    return (h * 360, s * 100, l * 100)


def hsl_to_hex(h, s, l):
    r_val, g_val, b_val = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r_val * 255):02x}{int(g_val * 255):02x}{int(b_val * 255):02x}"


START_HSL = hex_to_hsl(start_hex)
END_HSL = hex_to_hsl(end_hex)


def interpolate_hsl(hsl1, hsl2, t):
    h1, s1, l1 = hsl1
    h2, s2, l2 = hsl2
    dh = h2 - h1
    if dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    h = h1 + dh * t
    if h < 0:
        h += 360
    elif h >= 360:
        h -= 360
    s = s1 + (s2 - s1) * t
    l = l1 + (l2 - l1) * t
    return (h, s, l)


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


def diamond_petal_path(angle_deg):
    """菱形花瓣路径 - 四个顶点用直线连接"""
    # 菱形四个顶点（本地坐标）
    # 上顶点（尖端）
    top = rotate_translate(0, p1_y, angle_deg)
    # 下顶点（底部）
    bottom = rotate_translate(0, p2_y, angle_deg)
    # 左侧顶点
    left = rotate_translate(-side_x, side_y, angle_deg)
    # 右侧顶点
    right = rotate_translate(side_x, side_y, angle_deg)

    return (
        f"M {top[0]:.2f},{top[1]:.2f} "
        f"L {right[0]:.2f},{right[1]:.2f} "
        f"L {bottom[0]:.2f},{bottom[1]:.2f} "
        f"L {left[0]:.2f},{left[1]:.2f} Z"
    )


def diamond_mask_path(angle_deg):
    """菱形遮罩路径（膨胀后）"""
    # 遮罩的四个顶点
    top = rotate_translate(0, p1_y + delta, angle_deg)  # 向上膨胀
    bottom = rotate_translate(0, p2_y - delta, angle_deg)  # 向下膨胀
    left = rotate_translate(-side_x - delta * 0.5, side_y, angle_deg)  # 向左膨胀
    right = rotate_translate(side_x + delta * 0.5, side_y, angle_deg)  # 向右膨胀

    return (
        f"M {top[0]:.2f},{top[1]:.2f} "
        f"L {right[0]:.2f},{right[1]:.2f} "
        f"L {bottom[0]:.2f},{bottom[1]:.2f} "
        f"L {left[0]:.2f},{left[1]:.2f} Z"
    )


# 构建 SVG
big_rect = f"M {-svg_width},{-svg_height} h {svg_width * 2} v {svg_height * 2} h {-svg_width * 2} Z"

defs_parts = []
body_parts = []

for i, angle in enumerate(angles):
    t = i / 3
    color_hsl = interpolate_hsl(START_HSL, END_HSL, t)
    color_hex = hsl_to_hex(*color_hsl)

    petal_d = diamond_petal_path(angle)

    if i == 0:
        body_parts.append(f'    <path d="{petal_d}" fill="{color_hex}" />')
    else:
        prev_angle = angles[i - 1]
        mask_petal = diamond_mask_path(prev_angle)
        clip_id = f"clip-petal{i}"
        clip_path_d = f"{big_rect} {mask_petal}"

        defs_parts.append(
            f'    <clipPath id="{clip_id}">\n'
            f'      <path d="{clip_path_d}" clip-rule="evenodd" />\n'
            f"    </clipPath>"
        )

        body_parts.append(f'    <path d="{petal_d}" fill="{color_hex}" clip-path="url(#{clip_id})" />')

defs_svg = "\n".join(defs_parts)
petals_svg = "\n".join(body_parts)

svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
{defs_svg}
  </defs>
  <g transform="translate({center_x}, {center_y})">
{petals_svg}
  </g>
</svg>'''

with open("/Users/daisy/develop/blossom-slopware/flower_diamond.svg", "w") as f:
    f.write(svg_content)

print("菱形花朵 SVG 已生成: flower_diamond.svg")
print("菱形顶点位置（本地坐标）:")
print(f"  上顶点: (0, {p1_y:.2f})")
print(f"  下顶点: (0, {p2_y:.2f})")
print(f"  左顶点: (-{side_x:.2f}, 0)")
print(f"  右顶点: ({side_x:.2f}, 0)")
print(f"  宽高比: 宽 {2 * side_x:.2f} / 高 {2 * p1_y:.2f} = {side_x / p1_y:.2f}")
