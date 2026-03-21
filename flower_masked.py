import math

# 两个等圆的参数
r = 100  # 圆的半径
d = r * math.sqrt(2)  # 圆心距离，使得圆心角为 90 度

# 计算交点
intersection_y = math.sqrt(r**2 - (d/2)**2)
p1_y = intersection_y   # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）
petal_tip_distance = p1_y

# 花瓣角度：顺时针排列 — 左下(20°) → 左上(70°) → 右上(110°) → 右下(160°)
angles = [20, 70, 110, 160]
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2
mask_scale = 1.2


def transform_point(x, y, angle_deg, scale=1.0):
    """将花瓣本地坐标变换到花朵坐标系（含缩放，以几何中心为缩放中心）"""
    rotation = angle_deg + 90
    rot_rad = math.radians(rotation)
    sx, sy = x * scale, y * scale
    rx = sx * math.cos(rot_rad) - sy * math.sin(rot_rad)
    ry = sx * math.sin(rot_rad) + sy * math.cos(rot_rad)
    angle_rad = math.radians(angle_deg)
    offset_x = -petal_tip_distance * math.cos(angle_rad)
    offset_y = -petal_tip_distance * math.sin(angle_rad)
    return rx + offset_x, ry + offset_y


def petal_path_world(angle_deg, scale=1.0):
    """生成花瓣在花朵坐标系中的路径（含可选缩放）"""
    start = transform_point(0, p2_y, angle_deg, scale)
    mid = transform_point(0, p1_y, angle_deg, scale)
    scaled_r = r * scale
    return (
        f"M {start[0]:.2f},{start[1]:.2f} "
        f"A {scaled_r:.2f},{scaled_r:.2f} 0 0,1 {mid[0]:.2f},{mid[1]:.2f} "
        f"A {scaled_r:.2f},{scaled_r:.2f} 0 0,1 {start[0]:.2f},{start[1]:.2f} Z"
    )


# 构建 SVG
# 大矩形用于 evenodd 挖洞
big_rect = f"M {-svg_width},{-svg_height} h {svg_width*2} v {svg_height*2} h {-svg_width*2} Z"

defs_parts = []
body_parts = []

for i, angle in enumerate(angles):
    petal_d = petal_path_world(angle)

    if i == 0:
        # 第一个花瓣完整展示
        body_parts.append(
            f'    <path d="{petal_d}" fill="#FFB6C1" />'
        )
    else:
        # 前一花瓣以几何中心放大 1.2 倍作为遮罩
        prev_angle = angles[i - 1]
        mask_petal = petal_path_world(prev_angle, mask_scale)
        clip_id = f"clip-petal{i}"
        clip_path_d = f"{big_rect} {mask_petal}"

        defs_parts.append(
            f'    <clipPath id="{clip_id}">\n'
            f'      <path d="{clip_path_d}" clip-rule="evenodd" />\n'
            f'    </clipPath>'
        )

        body_parts.append(
            f'    <path d="{petal_d}" fill="#FFB6C1" clip-path="url(#{clip_id})" />'
        )

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

with open('/Users/daisy/develop/blossom-slopware/flower_masked.svg', 'w') as f:
    f.write(svg_content)

print("遮罩花朵 SVG 已生成: flower_masked.svg")
