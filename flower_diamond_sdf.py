import math
import colorsys

# ==================== 用户自定义颜色 ====================
start_hex = "#ffbfcd"
end_hex = "#ff99af"

# ==================== SDF 配置参数 ====================
# 菱形向中心缩小比例 (0-1)
shrink_ratio = 0.15
# SDF 阈值：距离缩小后菱形 ≤ D 的区域填充
# d = 8  # 可根据需要调整

# (y+d)/(x+d)=phi
# y+d= x phi + d phi
# d (phi - 1) = y-x phi
# d = (y-x phi)/(phi-1)
phi = 1.618

# ======================================================

# 两个等圆的参数
r = 100
d_circle = r * math.sqrt(2)

# 计算交点
intersection_y = math.sqrt(r**2 - (d_circle / 2) ** 2)
p1_y = intersection_y  # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）
petal_tip_distance = p1_y


# 菱形侧边顶点的 x 坐标
side_x = p1_y * 0.56

d = (p1_y - side_x * phi) / (phi - 1)


# 遮罩膨胀参数
diameter = 2 * r
delta = diameter / 24

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


def get_diamond_vertices(angle_deg, shrink=0.0):
    """获取菱形四个顶点，可选向中心收缩 shrink 比例"""
    # 原始顶点（本地坐标）
    top_local = (0, p1_y)
    bottom_local = (0, p2_y)
    left_local = (-side_x, 0)
    right_local = (side_x, 0)

    # 计算中心点
    center_local = (0, 0)

    # 向中心收缩
    factor = 1 - shrink
    top_local = (
        center_local[0] + (top_local[0] - center_local[0]) * factor,
        center_local[1] + (top_local[1] - center_local[1]) * factor,
    )
    bottom_local = (
        center_local[0] + (bottom_local[0] - center_local[0]) * factor,
        center_local[1] + (bottom_local[1] - center_local[1]) * factor,
    )
    left_local = (
        center_local[0] + (left_local[0] - center_local[0]) * factor,
        center_local[1] + (left_local[1] - center_local[1]) * factor,
    )
    right_local = (
        center_local[0] + (right_local[0] - center_local[0]) * factor,
        center_local[1] + (right_local[1] - center_local[1]) * factor,
    )

    # 转换到世界坐标
    top = rotate_translate(top_local[0], top_local[1], angle_deg)
    bottom = rotate_translate(bottom_local[0], bottom_local[1], angle_deg)
    left = rotate_translate(left_local[0], left_local[1], angle_deg)
    right = rotate_translate(right_local[0], right_local[1], angle_deg)

    return [top, right, bottom, left]


def point_to_segment_distance(px, py, x1, y1, x2, y2):
    """计算点 (px, py) 到线段 (x1,y1)-(x2,y2) 的距离"""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)


def point_in_diamond(px, py, vertices):
    """判断点是否在菱形内部（使用叉积法）"""
    n = len(vertices)
    inside = False
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        # 边向量
        ex = x2 - x1
        ey = y2 - y1
        # 点到起点的向量
        vx = px - x1
        vy = py - y1
        # 叉积
        cross = ex * vy - ey * vx
        # 对于凸多边形，所有叉积应该同号（假设顶点按顺时针或逆时针排列）
        # 这里简化处理：检查点是否在所有边的同一侧

    # 使用环绕数或射线法更简单
    # 射线法
    j = n - 1
    for i in range(n):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def diamond_sdf(px, py, vertices):
    """计算点到菱形的 SDF 值（内部为负，外部为正）"""
    # 计算到各边的距离，取最小
    min_dist = float("inf")
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        dist = point_to_segment_distance(px, py, x1, y1, x2, y2)
        min_dist = min(min_dist, dist)

    # 判断内外
    if point_in_diamond(px, py, vertices):
        return -min_dist
    return min_dist


def generate_sdf_polygon(angle_deg, shrink, d_threshold, num_samples=200):
    """
    生成 SDF ≤ d_threshold 的区域的多边形近似
    使用 Marching Squares 算法的简化版本
    """
    # 获取缩小后的菱形顶点
    shrunk_vertices = get_diamond_vertices(angle_deg, shrink)

    # 计算包围盒
    xs = [v[0] for v in shrunk_vertices]
    ys = [v[1] for v in shrunk_vertices]
    margin = d_threshold * 1.5
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin

    # 采样网格
    step = min(max_x - min_x, max_y - min_y) / num_samples

    # 收集 SDF ≤ d 的点作为轮廓
    contour_points = []

    # 使用更精确的方法：在圆周上采样，找到 SDF = d 的点
    center_x_local = sum(v[0] for v in shrunk_vertices) / 4
    center_y_local = sum(v[1] for v in shrunk_vertices) / 4

    # 从中心向外发射射线，找到 SDF = d 的边界点
    num_rays = 360
    for i in range(num_rays):
        angle = math.radians(i)
        # 从中心沿方向搜索
        t = 0
        max_t = max(max_x - min_x, max_y - min_y)
        found = False

        # 二分查找边界
        low, high = 0, max_t
        for _ in range(20):  # 迭代精度
            mid = (low + high) / 2
            px = center_x_local + math.cos(angle) * mid
            py = center_y_local + math.sin(angle) * mid
            sdf_val = diamond_sdf(px, py, shrunk_vertices)

            if sdf_val < d_threshold:
                low = mid
            else:
                high = mid

        boundary_x = center_x_local + math.cos(angle) * ((low + high) / 2)
        boundary_y = center_y_local + math.sin(angle) * ((low + high) / 2)
        contour_points.append((boundary_x, boundary_y))

    # 生成平滑的多边形路径
    if len(contour_points) < 3:
        return ""

    # 使用简化的多边形表示
    path = f"M {contour_points[0][0]:.2f},{contour_points[0][1]:.2f}"
    for i in range(1, len(contour_points)):
        path += f" L {contour_points[i][0]:.2f},{contour_points[i][1]:.2f}"
    path += " Z"

    return path


def generate_sdf_mask_polygon(angle_deg, shrink, d_threshold, delta_expand, num_rays=360):
    """
    生成遮罩路径：基于 SDF 花瓣再向外膨胀 delta_expand
    即：距离缩小后菱形 ≤ (d_threshold + delta_expand) 的区域
    """
    # 获取缩小后的菱形顶点
    shrunk_vertices = get_diamond_vertices(angle_deg, shrink)

    # 计算包围盒
    xs = [v[0] for v in shrunk_vertices]
    ys = [v[1] for v in shrunk_vertices]
    margin = (d_threshold + delta_expand) * 1.5
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin

    # 中心点
    center_x_local = sum(v[0] for v in shrunk_vertices) / 4
    center_y_local = sum(v[1] for v in shrunk_vertices) / 4

    # 新的阈值 = 原 SDF 阈值 + 膨胀距离
    mask_threshold = d_threshold + delta_expand

    # 从中心向外发射射线，找到 SDF = mask_threshold 的边界点
    contour_points = []
    for i in range(num_rays):
        angle = math.radians(i)
        max_t = max(max_x - min_x, max_y - min_y)

        # 二分查找边界
        low, high = 0, max_t
        for _ in range(20):
            mid = (low + high) / 2
            px = center_x_local + math.cos(angle) * mid
            py = center_y_local + math.sin(angle) * mid
            sdf_val = diamond_sdf(px, py, shrunk_vertices)

            if sdf_val < mask_threshold:
                low = mid
            else:
                high = mid

        boundary_x = center_x_local + math.cos(angle) * ((low + high) / 2)
        boundary_y = center_y_local + math.sin(angle) * ((low + high) / 2)
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

    # 生成 SDF 花瓣路径
    petal_d = generate_sdf_polygon(angle, shrink_ratio, d)

    if i == 0:
        body_parts.append(f'    <path d="{petal_d}" fill="{color_hex}" />')
    else:
        prev_angle = angles[i - 1]
        # 遮罩基于 SDF 花瓣再膨胀
        mask_petal = generate_sdf_mask_polygon(prev_angle, shrink_ratio, d, delta)
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

with open("/Users/daisy/develop/blossom-slopware/flower_diamond_sdf.svg", "w") as f:
    f.write(svg_content)

print("SDF 菱形花朵 SVG 已生成: flower_diamond_sdf.svg")
print(f"配置: 缩小比例 = {shrink_ratio}, SDF 阈值 d = {d}")
