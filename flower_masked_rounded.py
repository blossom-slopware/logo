import math
import colorsys

# ==================== 用户自定义颜色 ====================
start_hex = "#ffbfcd"
end_hex = "#ff99af"

# ==================== 圆角配置参数 ====================
# SDF 阈值：距离原始花瓣 ≤ d 的区域填充（形成圆角）
d = 12  # 可根据需要调整，越大圆角越明显

# ======================================================

# 两个等圆的参数
r = 100  # 圆的半径
d_circle = r * math.sqrt(2)  # 圆心距离，使得圆心角为 90 度

# 计算交点
intersection_y = math.sqrt(r**2 - (d_circle / 2) ** 2)
p1_y = intersection_y  # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）
petal_tip_distance = p1_y

# 遮罩膨胀参数
diameter = 2 * r
delta = diameter / 24

angles = [20, 70, 110, 160]
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2


def hex_to_hsl(hex_color):
    """HEX 转 HSL 颜色，返回 (h, s, l)"""
    hex_color = hex_color.lstrip("#")
    r_val = int(hex_color[0:2], 16) / 255.0
    g_val = int(hex_color[2:4], 16) / 255.0
    b_val = int(hex_color[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r_val, g_val, b_val)
    return (h * 360, s * 100, l * 100)


def hsl_to_hex(h, s, l):
    """HSL 转 HEX 颜色"""
    r_val, g_val, b_val = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r_val * 255):02x}{int(g_val * 255):02x}{int(b_val * 255):02x}"


START_HSL = hex_to_hsl(start_hex)
END_HSL = hex_to_hsl(end_hex)


def interpolate_hsl(hsl1, hsl2, t):
    """HSL 线性插值，t 在 [0, 1] 之间"""
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


def get_petal_center(angle_deg):
    """获取花瓣中心点（两个圆弧圆心的中点）"""
    # 两个圆弧的圆心位置（本地坐标）
    # 圆心1在 (-d/2, 0)，圆心2在 (d/2, 0)
    center1_local = (-d_circle / 2, 0)
    center2_local = (d_circle / 2, 0)

    # 转换到世界坐标
    center1 = rotate_translate(center1_local[0], center1_local[1], angle_deg)
    center2 = rotate_translate(center2_local[0], center2_local[1], angle_deg)

    # 花瓣中心是两圆心中点
    return ((center1[0] + center2[0]) / 2, (center1[1] + center2[1]) / 2)


def point_to_arc_distance(px, py, cx, cy, radius, start_angle, end_angle):
    """
    计算点 (px, py) 到圆弧的距离
    圆弧由圆心 (cx, cy)、半径、起始角度和结束角度定义
    """
    # 点到圆心的距离
    dx = px - cx
    dy = py - cy
    dist_to_center = math.sqrt(dx**2 + dy**2)

    # 点在圆上的角度
    point_angle = math.atan2(dy, dx)

    # 归一化角度到 [0, 2π]
    while point_angle < 0:
        point_angle += 2 * math.pi
    while start_angle < 0:
        start_angle += 2 * math.pi
    while end_angle < 0:
        end_angle += 2 * math.pi

    # 检查角度是否在圆弧范围内
    # 处理跨越 0 度的情况
    angle_in_range = False
    if start_angle <= end_angle:
        angle_in_range = start_angle <= point_angle <= end_angle
    else:
        angle_in_range = point_angle >= start_angle or point_angle <= end_angle

    if angle_in_range:
        # 点在圆弧角度范围内，距离是 |点到圆心距离 - 半径|
        return abs(dist_to_center - radius)
    else:
        # 点不在圆弧角度范围内，距离是到最近端点的距离
        start_x = cx + radius * math.cos(start_angle)
        start_y = cy + radius * math.sin(start_angle)
        end_x = cx + radius * math.cos(end_angle)
        end_y = cy + radius * math.sin(end_angle)

        dist_to_start = math.sqrt((px - start_x) ** 2 + (py - start_y) ** 2)
        dist_to_end = math.sqrt((px - end_x) ** 2 + (py - end_y) ** 2)
        return min(dist_to_start, dist_to_end)


def petal_sdf(px, py, angle_deg):
    """
    计算点到花瓣的 SDF 值（内部为负，外部为正）
    花瓣由两个圆弧组成
    """
    # 两个圆弧的圆心（本地坐标）
    center1_local = (-d_circle / 2, 0)
    center2_local = (d_circle / 2, 0)

    # 转换到世界坐标
    center1 = rotate_translate(center1_local[0], center1_local[1], angle_deg)
    center2 = rotate_translate(center2_local[0], center2_local[1], angle_deg)

    # 花瓣尖端和底部（世界坐标）
    tip = rotate_translate(0, p1_y, angle_deg)
    bottom = rotate_translate(0, p2_y, angle_deg)

    # 计算两个圆弧的角度范围
    # 圆弧1：从左下绕到左上
    angle_to_tip1 = math.atan2(tip[1] - center1[1], tip[0] - center1[0])
    angle_to_bottom1 = math.atan2(bottom[1] - center1[1], bottom[0] - center1[0])

    # 圆弧2：从左上绕到左下（或相反，取决于方向）
    angle_to_tip2 = math.atan2(tip[1] - center2[1], tip[0] - center2[0])
    angle_to_bottom2 = math.atan2(bottom[1] - center2[1], bottom[0] - center2[0])

    # 计算到两个圆弧的距离
    dist1 = point_to_arc_distance(px, py, center1[0], center1[1], r, angle_to_bottom1, angle_to_tip1)
    dist2 = point_to_arc_distance(px, py, center2[0], center2[1], r, angle_to_tip2, angle_to_bottom2)

    # 取最小距离
    min_dist = min(dist1, dist2)

    # 判断点是否在花瓣内部
    # 点在花瓣内部的条件：到两个圆心的距离都 <= r
    dist_to_c1 = math.sqrt((px - center1[0]) ** 2 + (py - center1[1]) ** 2)
    dist_to_c2 = math.sqrt((px - center2[0]) ** 2 + (py - center2[1]) ** 2)

    if dist_to_c1 <= r and dist_to_c2 <= r:
        return -min_dist
    return min_dist


def generate_rounded_petal(angle_deg, d_threshold, num_rays=360):
    """
    生成圆角花瓣路径：距离原始花瓣 ≤ d_threshold 的区域
    使用射线法找到 SDF = d_threshold 的边界点
    """
    # 获取花瓣中心
    petal_center = get_petal_center(angle_deg)

    # 估算包围盒
    tip = rotate_translate(0, p1_y, angle_deg)
    bottom = rotate_translate(0, p2_y, angle_deg)
    left = rotate_translate(-side_x if "side_x" in dir() else -d_circle / 2, 0, angle_deg)
    right = rotate_translate(side_x if "side_x" in dir() else d_circle / 2, 0, angle_deg)

    margin = d_threshold * 2
    max_dist = (
        max(
            math.sqrt((tip[0] - petal_center[0]) ** 2 + (tip[1] - petal_center[1]) ** 2),
            math.sqrt((bottom[0] - petal_center[0]) ** 2 + (bottom[1] - petal_center[1]) ** 2),
        )
        + margin
    )

    # 从中心向外发射射线，找到 SDF = d_threshold 的边界点
    contour_points = []
    for i in range(num_rays):
        angle = math.radians(i)

        # 二分查找边界
        low, high = 0, max_dist
        for _ in range(25):  # 迭代精度
            mid = (low + high) / 2
            px = petal_center[0] + math.cos(angle) * mid
            py = petal_center[1] + math.sin(angle) * mid
            sdf_val = petal_sdf(px, py, angle_deg)

            if sdf_val < d_threshold:
                low = mid
            else:
                high = mid

        boundary_x = petal_center[0] + math.cos(angle) * ((low + high) / 2)
        boundary_y = petal_center[1] + math.sin(angle) * ((low + high) / 2)
        contour_points.append((boundary_x, boundary_y))

    # 生成多边形路径
    if len(contour_points) < 3:
        return ""

    path = f"M {contour_points[0][0]:.2f},{contour_points[0][1]:.2f}"
    for i in range(1, len(contour_points)):
        path += f" L {contour_points[i][0]:.2f},{contour_points[i][1]:.2f}"
    path += " Z"

    return path


def generate_rounded_mask(angle_deg, d_threshold, delta_expand, num_rays=360):
    """
    生成圆角遮罩路径：基于圆角花瓣再向外膨胀 delta_expand
    即：距离原始花瓣 ≤ (d_threshold + delta_expand) 的区域
    """
    mask_threshold = d_threshold + delta_expand

    # 获取花瓣中心
    petal_center = get_petal_center(angle_deg)

    # 估算包围盒
    tip = rotate_translate(0, p1_y, angle_deg)
    bottom = rotate_translate(0, p2_y, angle_deg)

    margin = mask_threshold * 2
    max_dist = (
        max(
            math.sqrt((tip[0] - petal_center[0]) ** 2 + (tip[1] - petal_center[1]) ** 2),
            math.sqrt((bottom[0] - petal_center[0]) ** 2 + (bottom[1] - petal_center[1]) ** 2),
        )
        + margin
    )

    # 从中心向外发射射线，找到 SDF = mask_threshold 的边界点
    contour_points = []
    for i in range(num_rays):
        angle = math.radians(i)

        # 二分查找边界
        low, high = 0, max_dist
        for _ in range(25):
            mid = (low + high) / 2
            px = petal_center[0] + math.cos(angle) * mid
            py = petal_center[1] + math.sin(angle) * mid
            sdf_val = petal_sdf(px, py, angle_deg)

            if sdf_val < mask_threshold:
                low = mid
            else:
                high = mid

        boundary_x = petal_center[0] + math.cos(angle) * ((low + high) / 2)
        boundary_y = petal_center[1] + math.sin(angle) * ((low + high) / 2)
        contour_points.append((boundary_x, boundary_y))

    # 生成多边形路径
    if len(contour_points) < 3:
        return ""

    path = f"M {contour_points[0][0]:.2f},{contour_points[0][1]:.2f}"
    for i in range(1, len(contour_points)):
        path += f" L {contour_points[i][0]:.2f},{contour_points[i][1]:.2f}"
    path += " Z"

    return path


# 构建 SVG
big_rect = f"M {-svg_width},{-svg_height} h {svg_width * 2} v {svg_height * 2} h {-svg_width * 2} Z"

defs_parts = []
body_parts = []

for i, angle in enumerate(angles):
    t = i / 3
    color_hsl = interpolate_hsl(START_HSL, END_HSL, t)
    color_hex = hsl_to_hex(*color_hsl)

    # 生成圆角花瓣路径
    petal_d = generate_rounded_petal(angle, d)

    if i == 0:
        body_parts.append(f'    <path d="{petal_d}" fill="{color_hex}" />')
    else:
        prev_angle = angles[i - 1]
        # 遮罩基于圆角花瓣再膨胀
        mask_petal = generate_rounded_mask(prev_angle, d, delta)
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

with open("/Users/daisy/develop/blossom-slopware/flower_masked_rounded.svg", "w") as f:
    f.write(svg_content)

print("圆角花瓣 SVG 已生成: flower_masked_rounded.svg")
print(f"配置: SDF 阈值 d = {d}, 遮罩膨胀 delta = {delta}")
