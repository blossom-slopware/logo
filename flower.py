import math

# 两个等圆的参数
r = 100  # 圆的半径
d = r * math.sqrt(2)  # 圆心距离，使得圆心角为 90 度

# 计算交点
intersection_y = math.sqrt(r**2 - (d/2)**2)

# 交点坐标 (相对于花瓣中心)
p1_y = intersection_y   # 上交点（花瓣尖端）
p2_y = -intersection_y  # 下交点（花瓣底部）

# 花瓣尖端到中心的距离
petal_tip_distance = p1_y

# 构建单个花瓣的SVG路径 (垂直方向，尖端朝上，中心在原点)
# 路径: 从下交点开始 -> 沿左圆到上交点 -> 沿右圆到下交点 -> 闭合
path_d = f"M 0.00,{p2_y:.2f} A {r},{r} 0 0,1 0.00,{p1_y:.2f} A {r},{r} 0 0,1 0.00,{p2_y:.2f} Z"

# 花的参数
angles = [20, 70, 110, 160]  # 花瓣角度（相对于水平线）
svg_width = 800
svg_height = 800
center_x = svg_width / 2
center_y = svg_height / 2

# 生成花瓣 - 花瓣尖端对齐在花心
def create_petal(angle_deg):
    """创建一个旋转后的花瓣，尖端对齐在花心"""
    # 花瓣默认垂直，尖端朝上（指向 -y 方向在SVG中是向上）
    # 需要旋转使花瓣指向指定角度
    # 花瓣尖端朝上时，从中心到尖端的角度是 -90度
    # 所以旋转角度 = 目标角度 - (-90) = 目标角度 + 90
    rotation = angle_deg + 90
    
    # 计算花瓣尖端的位置（在旋转后的方向上）
    # 花瓣尖端原本在 (0, -petal_tip_distance) 相对于花瓣中心
    # 但我们需要花瓣尖端在花中心，所以花瓣中心需要偏移
    # 偏移方向与花瓣方向相反，距离为 petal_tip_distance
    angle_rad = math.radians(angle_deg)
    offset_x = -petal_tip_distance * math.cos(angle_rad)
    offset_y = -petal_tip_distance * math.sin(angle_rad)
    
    return f'<path d="{path_d}" fill="#FFB6C1" transform="translate({offset_x:.2f}, {offset_y:.2f}) rotate({rotation:.1f})" />'

# 创建SVG内容
petals_svg = "\n".join([f"    {create_petal(angle)}" for angle in angles])

svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 四瓣花，花瓣位于水平线夹角 20°, 70°, 110°, 160°，尖端对齐花心 -->
  <g transform="translate({center_x}, {center_y})">
{petals_svg}
  </g>
</svg>'''

# 保存 SVG 文件
with open('/Users/daisy/develop/blossom-slopware/flower.svg', 'w') as f:
    f.write(svg_content)

print("花朵 SVG 已生成: flower.svg")
print(f"花瓣角度: {angles}")
print(f"花瓣尖端对齐在花心，形成盛开的花朵")
