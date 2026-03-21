import math

# 两个等圆的参数
# 圆心距离 d = r * sqrt(2) 时，相交区域形成的"花瓣"形状最美观
# 此时两个圆的交点与各自圆心的连线形成 90 度角

r = 100  # 圆的半径
d = r * math.sqrt(2)  # 圆心距离，使得圆心角为 90 度

# 两个圆的圆心位置
# 将花瓣中心放在原点，两个圆心对称分布在 y 轴两侧
c1_x = -d / 2  # 左圆圆心
c1_y = 0
c2_x = d / 2   # 右圆圆心
c2_y = 0

# 计算交点
# 两个圆方程:
# (x - c1_x)^2 + (y - c1_y)^2 = r^2
# (x - c2_x)^2 + (y - c2_y)^2 = r^2

# 由于 c1_y = c2_y = 0，简化计算
# 交点的 y 坐标
# 由对称性，交点在 y 轴上，x = 0
# 代入第一个圆方程: (0 - c1_x)^2 + y^2 = r^2
# y^2 = r^2 - c1_x^2 = r^2 - (d/2)^2 = r^2 - (r*sqrt(2)/2)^2 = r^2 - r^2/2 = r^2/2

intersection_y = math.sqrt(r**2 - (d/2)**2)
intersection_x = 0

# 交点坐标
p1_x = 0
p1_y = intersection_y   # 上交点
p2_x = 0
p2_y = -intersection_y  # 下交点

# 计算圆弧的角度范围
# 对于左圆 (c1)，从 c1 看两个交点的角度
angle_c1_p1 = math.atan2(p1_y - c1_y, p1_x - c1_x)  # 从 c1 到上交点的角度
angle_c1_p2 = math.atan2(p2_y - c1_y, p2_x - c1_x)  # 从 c1 到下交点的角度

# 对于右圆 (c2)
angle_c2_p1 = math.atan2(p1_y - c2_y, p1_x - c2_x)  # 从 c2 到上交点的角度
angle_c2_p2 = math.atan2(p2_y - c2_y, p2_x - c2_x)  # 从 c2 到下交点的角度

# 转换为度数用于调试
# print(f"Left circle angles: {math.degrees(angle_c1_p1):.1f} to {math.degrees(angle_c1_p2):.1f}")
# print(f"Right circle angles: {math.degrees(angle_c2_p2):.1f} to {math.degrees(angle_c2_p1):.1f}")

# 生成 SVG 路径
# 花瓣由两段圆弧组成:
# 1. 从左圆的下交点顺时针到上交点 (大弧，但实际上是90度的小弧)
# 2. 从右圆的上交点顺时针到下交点

def polar_to_cartesian(cx, cy, r, angle):
    """将极坐标转换为笛卡尔坐标"""
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    return (x, y)

# 计算圆弧端点
# 左圆: 从 p2 (下交点) 到 p1 (上交点)，逆时针方向
left_start = polar_to_cartesian(c1_x, c1_y, r, angle_c1_p2)
left_end = polar_to_cartesian(c1_x, c1_y, r, angle_c1_p1)

# 右圆: 从 p1 (上交点) 到 p2 (下交点)，逆时针方向
right_start = polar_to_cartesian(c2_x, c2_y, r, angle_c2_p1)
right_end = polar_to_cartesian(c2_x, c2_y, r, angle_c2_p2)

# 构建 SVG 路径
# 使用 A 命令绘制圆弧
# A rx ry x-axis-rotation large-arc-flag sweep-flag x y
# large-arc-flag=0 表示小弧，sweep-flag=1 表示顺时针方向

# 路径: 从左下交点开始 -> 沿左圆到上交点 -> 沿右圆到右下交点 -> 闭合
path_d = f"M {p2_x:.2f},{p2_y:.2f} "  # 起点: 下交点
path_d += f"A {r},{r} 0 0,1 {p1_x:.2f},{p1_y:.2f} "  # 左圆弧线 (逆时针)
path_d += f"A {r},{r} 0 0,1 {p2_x:.2f},{p2_y:.2f} "  # 右圆弧线 (逆时针)
path_d += "Z"  # 闭合路径

# 创建 SVG
svg_width = 400
svg_height = 400
center_x = svg_width / 2
center_y = svg_height / 2

# 偏移量，将花瓣中心移到 SVG 中心
offset_x = center_x
offset_y = center_y

svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 花瓣形状: 两个90度圆心角的等圆相交区域 -->
  <path d="{path_d}" fill="#FFB6C1" transform="translate({offset_x}, {offset_y})" />
</svg>'''

# 保存 SVG 文件
with open('/Users/daisy/develop/blossom-slopware/petal.svg', 'w') as f:
    f.write(svg_content)

print("花瓣 SVG 已生成: petal.svg")
print(f"圆的半径: {r}")
print(f"圆心距离: {d:.2f} ( = r * √2 )")
print(f"交点: (0, ±{intersection_y:.2f})")
