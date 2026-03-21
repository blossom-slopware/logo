import math
import colorsys

# ==================== 用户自定义颜色 ====================
# 起始颜色 (HSL: 色相 0-360, 饱和度 0-100, 亮度 0-100)
start_hex = "#ffbfcd"
end_hex = "#ff99af"

# ======================================================

# 两个等圆的参数
r = 100  # 圆的半径
d = r * math.sqrt(2)  # 圆心距离，使得圆心角为 90 度

# 计算交点
intersection_y = math.sqrt(r**2 - (d / 2) ** 2)
p1_y = intersection_y  # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）
petal_tip_distance = p1_y

# 花瓣圆弧对应的直径
diameter = 2 * r
# 遮罩膨胀距离：直径的 1/24
delta = diameter / 24

# 膨胀后的遮罩参数（保持圆心不变，半径增大 delta）
r_mask = r + delta
mask_iy = math.sqrt(r_mask**2 - (d / 2) ** 2)

# 花瓣角度：顺时针排列 — 左下(20°) → 左上(70°) → 右上(110°) → 右下(160°)
angles = [20, 70, 110, 160]
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2


def hex_to_hsl(hex_color):
    """HEX 转 HSL 颜色，返回 (h, s, l)"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)


def hsl_to_hex(h, s, l):
    """HSL 转 HEX 颜色"""
    # h: 0-360, s: 0-100, l: 0-100
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# 计算起始和结束颜色的 HSL 值
START_HSL = hex_to_hsl(start_hex)
END_HSL = hex_to_hsl(end_hex)


def interpolate_hsl(hsl1, hsl2, t):
    """HSL 线性插值，t 在 [0, 1] 之间"""
    h1, s1, l1 = hsl1
    h2, s2, l2 = hsl2
    # 色相处理：选择最短路径
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


def petal_path_world(angle_deg):
    """花瓣在花朵坐标系中的路径"""
    start = rotate_translate(0, p2_y, angle_deg)
    end = rotate_translate(0, p1_y, angle_deg)
    return (
        f"M {start[0]:.2f},{start[1]:.2f} "
        f"A {r:.2f},{r:.2f} 0 0,1 {end[0]:.2f},{end[1]:.2f} "
        f"A {r:.2f},{r:.2f} 0 0,1 {start[0]:.2f},{start[1]:.2f} Z"
    )


def mask_path_world(angle_deg):
    """膨胀后遮罩在花朵坐标系中的路径"""
    start = rotate_translate(0, -mask_iy, angle_deg)
    end = rotate_translate(0, mask_iy, angle_deg)
    return (
        f"M {start[0]:.2f},{start[1]:.2f} "
        f"A {r_mask:.2f},{r_mask:.2f} 0 0,1 {end[0]:.2f},{end[1]:.2f} "
        f"A {r_mask:.2f},{r_mask:.2f} 0 0,1 {start[0]:.2f},{start[1]:.2f} Z"
    )


# 构建 SVG
big_rect = f"M {-svg_width},{-svg_height} h {svg_width * 2} v {svg_height * 2} h {-svg_width * 2} Z"

defs_parts = []
body_parts = []

# 四个花瓣的颜色（顺时针渐变）
for i, angle in enumerate(angles):
    t = i / 3  # 0, 1/3, 2/3, 1
    color_hsl = interpolate_hsl(START_HSL, END_HSL, t)
    color_hex = hsl_to_hex(*color_hsl)

    petal_d = petal_path_world(angle)

    if i == 0:
        body_parts.append(f'    <path d="{petal_d}" fill="{color_hex}" />')
    else:
        prev_angle = angles[i - 1]
        mask_petal = mask_path_world(prev_angle)
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

with open("/Users/daisy/develop/blossom-slopware/flower_masked.svg", "w") as f:
    f.write(svg_content)

print("遮罩花朵 SVG 已生成: flower_masked.svg")
print(f"起始颜色 (HSL): {START_HSL} -> {hsl_to_hex(*START_HSL)}")
print(f"末尾颜色 (HSL): {END_HSL} -> {hsl_to_hex(*END_HSL)}")
print("四个花瓣颜色:")
for i in range(4):
    t = i / 3
    c = hsl_to_hex(*interpolate_hsl(START_HSL, END_HSL, t))
    print(f"  花瓣 {i + 1}: {c}")
